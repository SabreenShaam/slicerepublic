from accounts.models import MboClientSettings
from classes.models import Program
from slice.models import SliceService, SliceServiceProgram
from bookings.bookings_core.models import Booking, ExternalBookingService, UnpaidBookings

from mind_body_service.classes_api import add_client_to_class
from mind_body_service.sale_api import purchase_complementary_item_and_add_client_to_class

from bookings.bookings_api.tasks import send_upcoming_booking_reminder
from ratings.tasks import send_rating_notification

from classes.mbo_class_service import MboGetClassVisit

from slice.exceptions import SliceServiceDoesNotExistException

from django.conf import settings

from abc import ABC, abstractmethod

import logging
from datetime import timedelta, datetime
from slicerepublic import dateutil


class Booker(ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, mbo_class, client_id):
        self.mbo_class = mbo_class
        self.site_id = mbo_class.get_site_id()
        self.class_id = mbo_class.get_class_id()
        self.client_id = client_id

    @abstractmethod
    def make_booking(self):
        pass

    def get_visit(self):
        visits = MboGetClassVisit(self.site_id, self.class_id)
        client_visit = visits.get_visit_for_given_client(self.client_id)
        return client_visit

    def create_booking(self, slice_class, mbo_client):
        visit = self.get_visit()
        booking = Booking.objects.create_booking(mbo_client, slice_class, visit.ID, False, Booking.SYNCHED_STATUS)
        self.logger.debug("Booking created (booking_id : {})".format(booking.id))
        return booking

    @staticmethod
    def schedule_upcoming_booking_reminder(mbo_client_id, booking_id, slice_class):
        mbo_client_setting = MboClientSettings.objects.get_mbo_client_settings(mbo_client_id)
        if mbo_client_setting and mbo_client_setting.remind_classes:
            start_date = slice_class.start_date
            start_time = slice_class.start_time
            scheduled_dt = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute) + timedelta(hours=-2)
            localized_time = dateutil.localize(scheduled_dt)
            send_upcoming_booking_reminder.apply_async((booking_id, mbo_client_id), eta=localized_time)


class InternalBooker(Booker):
    logger = logging.getLogger(__name__)

    def make_booking(self):
        if self.mbo_class.has_free_web_slot():
            add_client_to_class(self.client_id, self.site_id, self.class_id)
            self.logger.debug("Booked into class {} in studio {} for client {}".format(self.class_id,
                                                                                       self.site_id,
                                                                                       self.client_id))
        return True


class ExternalBooker(Booker):
    logger = logging.getLogger(__name__)

    def __init__(self, mbo_class, client_id, external_studio, slice_class):
        super(ExternalBooker, self).__init__(mbo_class, client_id)
        self.studio = external_studio
        self.slice_class = slice_class

    def __get_slice_service(self):
        slice_services = SliceServiceProgram.objects.get_slice_services_by_program(self.slice_class.program)
        if len(slice_services) == 0:
            message = "Slice service does not exist for the studio {}".format(self.studio.name)
            self.logger.error(message)
            raise SliceServiceDoesNotExistException("30000", "Slice service not found", message)
        return slice_services[0].slice_service

    def make_booking(self):
        slice_service = self.__get_slice_service()
        if self.mbo_class.has_free_slot():
            self.logger.debug("{} , {} , {} , {}".format(self.class_id, self.client_id, slice_service.mbo_service_id, self.site_id))
            purchase_complementary_item_and_add_client_to_class(self.class_id,
                                                                self.client_id,
                                                                slice_service.mbo_service_id,
                                                                self.site_id,
                                                                settings.MBO_STAFF_USERNAME,
                                                                settings.MBO_STAFF_PASSWORD)
            self.logger.debug("Booked into class {} in studio {} for client {}".format(self.class_id,
                                                                                       self.site_id,
                                                                                       self.client_id))

    def create_booking(self, slice_class, mbo_client, mbo_client_service, is_paid):
        # Create a Booking record
        booking = super(ExternalBooker, self).create_booking(slice_class, mbo_client)

        # Create an ExternalBookingService and UnpaidBookings mapping record
        if is_paid:
            ExternalBookingService.objects.create_external_booking(booking, mbo_client_service)
        else:
            UnpaidBookings.objects.create(booking=booking, parent_service=mbo_client_service)
        return booking

