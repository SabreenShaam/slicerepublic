from django.core.paginator import Paginator, EmptyPage
from accounts.exceptions import MembershipRequiredException
from accounts.models import MboClient, MboExternalClient, UserExternalStudio
from bookings.bookings_api.credits import Credits
from bookings.bookings_api.rules import OverFlowRule, ExternalCountRule, MaximumPerStudioRule
from bookings.bookings_core.models import Booking, UnpaidBookings
from classes.models import SliceClass, Program

from bookings.bookings_api.booker import InternalBooker, ExternalBooker

from accounts.mbo_client_manager import MboClientManager
from services.models import MboService, MboClientService
from services.passport_service import PassportService
from services.pricing_option import PricingOption
from slicerepublic.dateutil import is_within_date_range

from staff.serializers import StaffSerializer

from bookings.bookings_core.exceptions import LateCancelException, ExternalLateCancelException

from mind_body_service.classes_api import get_class_visits, update_client_visits, client_sign_in
from mind_body_service.client_api import get_client_visits

from venues.venue_manager import get_number_of_locations_of_studios
from classes.class_manager import is_within_sign_in_period, handle_room_location, populate_class_studio_info, \
    populate_class_location_info
from services.service_manager import get_required_services_for_external_bookings, sync_mbo_client_services, \
    settle_unpaid_bookings

from slicerepublic.distance_util import is_inside_radius
from slicerepublic import dateutil
from slicerepublic.sendmail import send_booking_confirmation_mail_member, send_booking_cancellation_mail_member

from classes.mbo_class_service import MboGetClass

from django.conf import settings
from datetime import timedelta, datetime
from bookings.bookings_api.utils import is_paid_booking

from ratings.ClassRating import ClassRating

from venues import venues_dao
from django.core.cache import cache
from django.db import transaction
import time
import math

import logging

logger = logging.getLogger(__name__)


def book_class(slice_class, user, home_studio):
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=home_studio)

    logger.info("Entered book_class (mbo_site_id : {}, mbo_class_id : {}, mbo_client_id : {})".
                format(slice_class.studio.mbo_site_id, slice_class.mbo_class_id, mbo_client.mbo_client_id))

    mbo_class = MboGetClass(slice_class.studio.mbo_site_id, slice_class.mbo_class_id, slice_class.start_date,
                            slice_class.end_date)
    mbo_class.is_empty()

    booking = None

    # internal booking
    if mbo_client.is_home_studio(slice_class.studio):
        pricing_option = PricingOption(mbo_client)
        pricing_option.get_current_service()
        internal_booker = InternalBooker(mbo_class, mbo_client.mbo_client_id)
        internal_booker.make_booking()
        booking = internal_booker.create_booking(slice_class, mbo_client)
        send_booking_confirmation_mail_member(booking, user.email)

        pricing_option.handle_auto_pay()

        #InternalBooker.schedule_upcoming_booking_reminder(mbo_client.id, booking.id, slice_class)
        ClassRating.schedule_rating_notification(mbo_client.id, booking.id, slice_class)
    else:  # external booking
        mbo_client_services = list(PassportService.fetch_all_active_passport_services(mbo_client, slice_class.studio))

        if len(mbo_client_services) == 0:
            sync_mbo_client_services(mbo_client)
            mbo_client_services = list(PassportService.fetch_all_active_passport_services(mbo_client, slice_class.studio))

        mbo_client_services_original = list(mbo_client_services)

        if len(mbo_client_services_original) == 0:
            __raise_exception(mbo_client)

        for mbo_client_service in mbo_client_services:
            mbo_service = MboService.objects.get_mbo_service_by_name_and_studio(mbo_client_service.name,
                                                                                mbo_client.studio)
            overflow_rule = OverFlowRule(mbo_client_services_original, mbo_client_service, mbo_service,
                                         slice_class.start_date)
            external_count_rule = ExternalCountRule(mbo_client_services_original, mbo_client, mbo_client_service,
                                                    mbo_service, slice_class.start_date)
            maximum_per_studio_rule = MaximumPerStudioRule(mbo_client_services_original, mbo_client, mbo_client_service,
                                                           mbo_service, slice_class.start_date, slice_class.studio)

            overflow_rule.next_rule = external_count_rule
            external_count_rule.next_rule = maximum_per_studio_rule
            overflow_rule.check()

        if len(mbo_client_services_original) == 0:
            __raise_exception(mbo_client)

        selected_mbo_client_service = None
        for mbo_client_service in mbo_client_services_original:
            if is_paid_booking(mbo_client_service, slice_class.start_date):
                selected_mbo_client_service = mbo_client_service
                break
            else:
                if not selected_mbo_client_service:
                    selected_mbo_client_service = mbo_client_service

        if len(mbo_client_services_original) == 0:
            __raise_exception(mbo_client)

        mbo_external_client = ExternalClientHandler.get_external_client(user, slice_class.studio)
        external_booker = ExternalBooker(mbo_class, mbo_external_client.mbo_client_id, slice_class.studio, slice_class)
        external_booker.make_booking()

        is_paid = False
        if is_paid_booking(selected_mbo_client_service, slice_class.start_date):
            is_paid = True

        booking = external_booker.create_booking(slice_class, mbo_client, selected_mbo_client_service, is_paid)
        send_booking_confirmation_mail_member(booking, user.email)

        #ExternalBooker.schedule_upcoming_booking_reminder(mbo_client.id, booking.id, slice_class)
        ClassRating.schedule_rating_notification(mbo_client.id, booking.id, slice_class)
    logger.info("Leaving book_class")

    return booking


class ExternalClientHandler(object):
    @staticmethod
    def get_external_client(user, studio):
        local_external_client = MboExternalClient.objects.get_mbo_external_client_by_user(user)
        if not local_external_client:
            local_external_client = ExternalClientHandler.create_local_external_client(user)
            mbo_client_manager = MboClientManager()
            mbo_client_manager.__int__()
            mbo_client_manager.create_external_client(studio.mbo_site_id, user)
            UserExternalStudio.objects.create(user=user, studio=studio)
        else:
            user_external_studio = UserExternalStudio.objects.get_user_external_studio_by_user_and_studio(user, studio)
            if not user_external_studio:
                mbo_client_manager = MboClientManager()
                mbo_client_manager.__int__()
                mbo_client_manager.create_external_client(studio.mbo_site_id, user)
                UserExternalStudio.objects.create(user=user, studio=studio)

        return local_external_client

    @staticmethod
    def create_local_external_client(user):
        mbo_client_id = MboClientManager.generate_client_id(user.id)
        email = MboClientManager.generate_email(mbo_client_id)
        mbo_external_client = MboExternalClient.objects.create(user=user, mbo_client_id=mbo_client_id, email=email)
        return mbo_external_client


def get_new_visit(slice_mbo_client_id, slice_class_id, mbo_class_id, studio):
    logger.info("Entered get_new_visit (slice_mbo_client_id : {}, slice_class_id : {}, mbo_class_id : {}, "
                "studio : {}".format(slice_mbo_client_id, slice_class_id, mbo_class_id, studio.name))
    result = get_class_visits(mbo_class_id, studio.mbo_site_id)
    slice_client_visits = []
    for visit in result.Class.Visits.Visit:
        if visit.Client.ID == slice_mbo_client_id:
            slice_client_visits.append(visit)

    existing_class_visit_ids = Booking.objects.get_class_bookings(mbo_class_id, studio)

    new_visit = None
    for visit in slice_client_visits:
        if visit.ID in existing_class_visit_ids:
            continue
        else:
            new_visit = visit
            break

    logger.info("Leaving get_new_visit (visit id : {})".format(new_visit.ID))
    return new_visit


def get_client_visit(mbo_site_id, mbo_class_id, mbo_client_id):
    logger.info("Entered get_client_visit (mbo_site_id : {}, mbo_class_id : {}, mbo_client_id : {})".
                format(mbo_site_id, mbo_class_id, mbo_client_id))
    result = get_class_visits(mbo_class_id, mbo_site_id)
    for visit in result.Class.Visits.Visit:
        if visit.Client.ID == mbo_client_id:
            logger.info("Leaving get_client_visit (visit id : {})".format(visit.ID))
            return visit
    logger.error("No visits found in the class!")


def cancel_booking(booking, user, studio, late_cancel):
    logger.info("Entered cancel_booking (booking id : {}, user id : {})".format(booking.id, user.id))
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)

    # todo : check how many db calls are there in this query
    mbo_site_id = booking.slice_class.studio.mbo_site_id

    cancelled_by = '{} {}'.format(user.first_name, user.last_name)
    cancelled_date = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London").date()

    if late_cancel:
        if late_cancel == "false":
            cancel_off_set = 1440
            if mbo_client.studio.mbo_site_id == mbo_site_id:
                cancel_off_set = booking.slice_class.program.cancel_off_set

            if is_late_cancel(booking.slice_class.start_date, booking.slice_class.start_time, cancel_off_set):
                if not is_cancelled_within_five_minutes(booking):
                    message = "Cancellation is outside allowed window."
                    logger.debug(message)
                    raise LateCancelException("70040", "Cancellation failed", message)

            # Use mbo_visit_id to cancel booking, using staff credentials as we check late cancel
            update_client_visits(booking.mbo_visit_id, mbo_site_id, 'cancel', settings.MBO_STAFF_USERNAME,
                                 settings.MBO_STAFF_PASSWORD)
            booking.is_cancelled = True
            send_booking_cancellation_mail_member(booking, cancelled_by, cancelled_date, user.email)
        elif late_cancel == "true":
            # Use mbo_visit_id to cancel booking, using staff credentials as we check late cancel
            update_client_visits(booking.mbo_visit_id, mbo_site_id, 'latecancel', settings.MBO_STAFF_USERNAME,
                                 settings.MBO_STAFF_PASSWORD)
            booking.late_cancelled = True
    else:
        cancel_off_set = 1440
        if mbo_client.studio.mbo_site_id == mbo_site_id:
            cancel_off_set = booking.slice_class.program.cancel_off_set

        if is_late_cancel(booking.slice_class.start_date, booking.slice_class.start_time, cancel_off_set):
            if not is_cancelled_within_five_minutes(booking):
                message = "Cancellation is outside allowed window."
                logger.info(message)
                if mbo_client.studio.mbo_site_id != mbo_site_id:
                    raise ExternalLateCancelException("70050", "Late Cancellation failed", message)
                raise LateCancelException("70040", "Late Cancellation failed", message)

        # Use mbo_visit_id to cancel booking, using staff credentials as we check late cancel
        update_client_visits(booking.mbo_visit_id, mbo_site_id, 'cancel', settings.MBO_STAFF_USERNAME,
                             settings.MBO_STAFF_PASSWORD)
        booking.is_cancelled = True
        send_booking_cancellation_mail_member(booking, cancelled_by, cancelled_date, user.email)

    booking.save()
    logger.info("Leaving cancel_booking.")
    return booking


def get_upcoming_bookings(user, studio):
    logger.info("Entered get_upcoming_bookings (user id : {})".format(user.id))

    local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    current_date = local_dt.date()
    current_time = local_dt.time()

    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)
    sync_client_bookings(mbo_client)

    result = Booking.objects.get_upcoming_classes(mbo_client.id, current_date, current_time)

    logger.info("Leaving get_upcoming_bookings (Number of results : {})".format(result.count()))
    return result


def get_past_bookings(user, studio):
    logger.info("Entered get_past_bookings (user id : {})".format(user.id))

    local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    current_date = local_dt.date()
    current_time = local_dt.time()

    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)
    sync_client_bookings(mbo_client)
    result = Booking.objects.get_past_classes(mbo_client.id, current_date, current_time)

    logger.info("Leaving get_past_bookings (Number of results : {})".format(result.count()))
    return result


def get_mbo_client_visits(mbo_client_id, mbo_site_id, start_date, end_date):
    logger.info("Entered get_mbo_client_visits (mbo_client_id : {}, mbo_site_id : {}, start_date : {}, end_date : {})"
                .format(mbo_client_id, mbo_site_id, start_date, end_date))

    response = get_client_visits(staff_username=settings.MBO_STAFF_USERNAME,
                                 staff_password=settings.MBO_STAFF_PASSWORD,
                                 mbo_client_id=mbo_client_id,
                                 start_date=start_date,
                                 end_date=end_date,
                                 mbo_site_id=mbo_site_id)

    if isinstance(response.Visits, str):
        return None
    logger.info("Leaving get_mbo_client_visits. count : {}".format(len(response.Visits.Visit)))
    return response.Visits.Visit


def sync_client_visits(mbo_client, start_date, end_date):
    logger.info("Entered sync_client_visits (mbo_client_id : {}, start_date : {}, end_date : {})"
                .format(mbo_client.mbo_client_id, start_date, end_date))

    mbo_client_visits = get_mbo_client_visits(mbo_client.mbo_client_id, mbo_client.studio.mbo_site_id, start_date,
                                              end_date)
    result = Booking.objects.get_bookings_by_mbo_client_site_and_date_range(mbo_client.id, mbo_client.studio,
                                                                            start_date, end_date)

    if mbo_client_visits is None:
        if len(result) > 0:
            for booking in result:
                if not booking.is_cancelled and not booking.late_cancelled:
                    booking.sync_status = Booking.UNKNOWN_STATUS
                    booking.save()
    else:
        if len(result) == 0:
            for visit in mbo_client_visits:
                slice_class = SliceClass.objects.get_class_by_mbo_class_id_and_studio(
                    mbo_class_id=visit.ClassID, studio=mbo_client.studio)

                if slice_class:
                    booking = Booking()
                    booking.mbo_client = mbo_client
                    booking.slice_class_id = slice_class.id
                    booking.mbo_visit_id = visit.ID
                    booking.late_cancelled = visit.LateCancelled
                    booking.signed_in = visit.SignedIn
                    booking.sync_status = Booking.SYNCHED_STATUS
                    booking.save()
        elif len(result) > 0:
            for visit in mbo_client_visits:
                found = False

                for booking in result:
                    if visit.ID == booking.mbo_visit_id:
                        if booking.late_cancelled != visit.LateCancelled:
                            booking.late_cancelled = visit.LateCancelled
                            booking.save()
                        if booking.signed_in != visit.SignedIn:
                            booking.signed_in = visit.SignedIn
                            booking.save()
                        if booking.sync_status != Booking.SYNCHED_STATUS:
                            booking.sync_status = Booking.SYNCHED_STATUS
                            booking.save()
                        found = True

                if not found:
                    slice_class = SliceClass.objects.get_class_by_mbo_class_id_and_studio(
                        mbo_class_id=visit.ClassID, studio=mbo_client.studio)

                    if slice_class:
                        booking = Booking()
                        booking.mbo_client = mbo_client
                        booking.slice_class_id = slice_class.id
                        booking.mbo_visit_id = visit.ID
                        # If a booking is late canceled, GetClientVisits API call does not return that record.
                        booking.late_cancelled = visit.LateCancelled
                        booking.signed_in = visit.SignedIn
                        booking.sync_status = Booking.SYNCHED_STATUS
                        booking.save()

            for booking in result:
                found = False
                for visit in mbo_client_visits:
                    if visit.ID == booking.mbo_visit_id:
                        found = True
                if not found:
                    if not booking.is_cancelled and not booking.late_cancelled:
                        booking.sync_status = Booking.UNKNOWN_STATUS
                        booking.save()
    logger.info("Leaving sync_client_visits.")


def get_upcoming_booking_response(bookings, lat, lng):
    results = venues_dao.get_studios_with_settings()
    studios = {}
    # result[0] = id, result[1] = name, result[2] = room_location_enabled
    for result in results:
        studios[result[0]] = result

    studio_location_count = get_number_of_locations_of_studios()
    booking_item_list = []
    for booking in bookings:
        studio = studios[booking.slice_class.studio_id]
        booking_item = populate_booking(booking, studio_location_count, studio, 'upcoming')
        use_mbo_location = booking_item.pop("use_mbo_location", False)

        if is_within_sign_in_period(booking.slice_class.start_date, booking.slice_class.start_time):
            if not booking.signed_in:
                if lat and lng:
                    if use_mbo_location:
                        allow_sign_in = is_inside_radius(booking.slice_class.mbolocation.location.latitude,
                                                         booking.slice_class.mbolocation.location.longitude,
                                                         lat, lng)
                        if allow_sign_in:
                            booking_item['action'] = 'sign_in'
                    elif ('latitude' in booking_item['location']) and ('longitude' in booking_item['location']):
                        allow_sign_in = is_inside_radius(booking_item['location']['latitude'],
                                                         booking_item['location']['longitude'], lat, lng)
                        if allow_sign_in:
                            booking_item['action'] = 'sign_in'

        booking_item_list.append(booking_item)
    return booking_item_list


def get_past_bookings_response(bookings):
    results = venues_dao.get_studios_with_settings()
    studios = {}
    # result[0] = id, result[1] = name, result[2] = room_location_enabled
    for result in results:
        studios[result[0]] = result

    studio_location_count = get_number_of_locations_of_studios()
    booking_item_list = []
    for booking in bookings:
        studio = studios[booking.slice_class.studio_id]
        booking_item = populate_booking(booking, studio_location_count, studio, 'past')
        booking_item_list.append(booking_item)
    return booking_item_list


def sign_in(booking):
    logger.info("Entered sign in (booking id : {})".format(booking.id))

    if booking.signed_in:
        logger.info("Already signed in!")
        return
    # todo : can eliminate db call booking.slice_class.studio.mbo_site_id
    client_sign_in(mbo_visit_id=booking.mbo_visit_id,
                   mbo_site_id=booking.slice_class.studio.mbo_site_id,
                   signed_in=True,
                   staff_username=settings.MBO_STAFF_USERNAME,
                   staff_password=settings.MBO_STAFF_PASSWORD)

    booking.signed_in = True
    booking.save()

    logger.info("Signed in for class {}".format(booking.slice_class.name))


def get_sign_in_response(booking):
    # todo : are we using this anymore
    studio_location_count = get_number_of_locations_of_studios()
    response = populate_sign_in_booking(booking, studio_location_count)
    return response


def populate_booking(booking, studio_location_count, studio, booking_type):
    booking_item = {}
    booking_item['id'] = booking.id

    if booking_type == 'upcoming':
        booking_item['use_mbo_location'] = True
        booking_item['action'] = 'cancel'
        if booking.signed_in:
            booking_item['action'] = 'arrived'

    booking_item['staff'] = StaffSerializer(booking.slice_class.staff).data

    slice_class = {}
    populate_class_basic_info(slice_class, booking.slice_class)

    duration = dateutil.time_diff(booking.slice_class.end_time, booking.slice_class.start_time)
    # Duration is in minutes
    slice_class['duration'] = duration.seconds / 60

    booking_item['slice_class'] = slice_class

    if studio[2]:
        handle_room_location(booking.slice_class, booking_item)
        if booking_type == 'upcoming':
            booking_item['use_mbo_location'] = False
    else:
        populate_class_studio_info(booking_item, booking.slice_class.studio)
        populate_class_location_info(booking_item, booking.slice_class.mbolocation.location)
        if studio_location_count[booking.slice_class.studio_id] > 1:
            booking_item['multilocation'] = True
        else:
            booking_item['multilocation'] = False

    return booking_item


def populate_class_basic_info(class_item, slice_class):
    class_item['id'] = slice_class.id
    class_item['name'] = slice_class.name
    class_item['start_date'] = slice_class.start_date
    class_item['end_date'] = slice_class.end_date
    class_item['start_time'] = slice_class.start_time
    class_item['end_time'] = slice_class.end_time


def populate_sign_in_booking(booking, studio_location_count):
    booking_item = {}
    booking_item['id'] = booking.id

    slice_class = {}
    slice_class['id'] = booking.slice_class.id
    slice_class['bookable'] = booking.slice_class.bookable
    slice_class['name'] = booking.slice_class.name
    slice_class['description'] = booking.slice_class.description
    slice_class['start_date'] = booking.slice_class.start_date
    slice_class['end_date'] = booking.slice_class.end_date
    slice_class['start_time'] = booking.slice_class.start_time
    slice_class['end_time'] = booking.slice_class.end_time

    duration = dateutil.time_diff(booking.slice_class.end_time, booking.slice_class.start_time)

    # Duration is in minutes
    slice_class['duration'] = duration.seconds / 60

    booking_item['slice_class'] = slice_class

    location = {}
    if studio_location_count[booking.slice_class.studio_id] > 1:
        location["name"] = "{} - {}".format(booking.slice_class.studio.name,
                                            booking.slice_class.mbolocation.location.name)
    else:
        location["name"] = booking.slice_class.studio.name
    location["city"] = booking.slice_class.mbolocation.location.city

    booking_item['staff'] = StaffSerializer(booking.slice_class.staff).data
    booking_item['location'] = location
    booking_item['signed_in'] = booking.signed_in
    return booking_item


def is_late_cancel(start_date, start_time, mins):
    start_dt = datetime.combine(start_date, start_time)
    diff_minutes = dateutil.get_local_diff_in_minute(start_dt, dateutil.utcnow())
    if diff_minutes < 0:
        pass
    elif diff_minutes < mins:
        return True
    elif diff_minutes > mins:
        return False


def is_cancelled_within_five_minutes(booking):
    created_timestamp = time.mktime(booking.created.timetuple())
    current_timestamp = time.mktime(dateutil.utcnow().timetuple())
    diff_minutes = math.ceil((current_timestamp - created_timestamp) / 60)
    if diff_minutes <= 5:
        return True
    return False

"""This method outputs the total number of external bookings within the expiration date"""


def get_external_bookings_by_mbo_client(mbo_client):
    studio_id = mbo_client.studio.id
    mbo_client_services = get_required_services_for_external_bookings(mbo_client)
    if mbo_client_services:
        for mbo_client_service in mbo_client_services:
            external_bookings = Booking.objects.get_external_bookings_count_for_service(mbo_client.id, studio_id,
                                                                                        mbo_client_service[
                                                                                            'active_date'],
                                                                                        mbo_client_service[
                                                                                            'expire_date'])
        if external_bookings:
            return external_bookings
    return None


"""to check whether sync needed or not"""


def sync_client_bookings(mbo_client):
    start_dt = dateutil.get_local_datetime(dateutil.utcnow_plus(timedelta(days=-60)), "Europe/London")
    end_dt = dateutil.get_local_datetime(dateutil.utcnow_plus(timedelta(days=14)), "Europe/London")
    current_datetime = dateutil.utcnow()

    if not cache.get('key_booking_history_' + str(mbo_client.id)):
        sync_client_visits(mbo_client, start_dt.date(), end_dt.date())

        client_bookings_dict = {'sync_name': 'client_bookings', 'id': mbo_client.id, 'datetime': current_datetime}
        cache.set('key_booking_history_' + str(mbo_client.id), client_bookings_dict,
                  settings.CLIENT_BOOKINGS_SYNC_TIMEOUT)


# """Get total number of external bookings"""

#
# def get_total_number_of_external_bookings(mbo_client):
#     external_bookings = get_external_bookings_by_mbo_client(mbo_client)
#     if external_bookings:
#         return external_bookings
#     return 0

"""populate booking credits item"""


def populate_external_booking_credits_details(user, studio):
    external_credit_list = []
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)
    mbo_client_services = get_required_services_for_external_bookings(mbo_client)
    for mbo_client_service in mbo_client_services:
        mbo_service = MboService.objects.get_mbo_service_by_name_and_studio(mbo_client_service['name'], studio)
        external_credits_count = Credits.get_used_external_credits_by_service(mbo_client, mbo_client_service['id'])
        external_credit_item = {}
        external_credit_item['name'] = mbo_client_service['name']
        external_credit_item['expiration_date'] = mbo_client_service['expire_date']
        external_credit_item['count'] = mbo_service.count

        remaining = mbo_service.count - external_credits_count
        if remaining > 0:
            external_credit_item['remaining'] = remaining
        else:
            external_credit_item['remaining'] = 0

        external_credit_list.append(external_credit_item)
    return external_credit_list


def __raise_exception(mbo_client):
    message = "You have used your external class allowance. To buy additional credits please visit your accounts page for further options"
    logger.error("{} (username : {})".format(message, mbo_client.user.get_username()))
    raise MembershipRequiredException("40070", "Membership required.", message)


@transaction.atomic
def handle_unpaid_bookings():
    mbo_client_set = set()
    unpaid_bookings = UnpaidBookings.objects.get_active_unpaid_bookings()
    current_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    for unpaid_booking in unpaid_bookings:
        sync_client_services(mbo_client_set, unpaid_booking.booking.mbo_client)
        parent_service = unpaid_booking.parent_service
        mbo_client_service = MboClientService.objects.get_service_by_name_and_payment_date(
            unpaid_booking.booking.mbo_client, parent_service.name, parent_service.expiration_date)
        if mbo_client_service:
            settle_unpaid_bookings(unpaid_booking, mbo_client_service)
            continue

        booking = unpaid_booking.booking

        mbo_site_id = unpaid_booking.booking.slice_class.studio.mbo_site_id
        if parent_service.expiration_date < current_dt.date():
            update_client_visits(booking.mbo_visit_id, mbo_site_id, 'cancel', settings.MBO_STAFF_USERNAME,
                                 settings.MBO_STAFF_PASSWORD)
            booking.cancel()


def sync_client_services(mbo_client_set, mbo_client):
    if mbo_client not in mbo_client_set:
        sync_mbo_client_services(mbo_client)
        mbo_client_set.add(mbo_client)


def get_total_external_unpaid_bookings_count(user, studio):
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)
    count = Credits.get_total_external_unpaid_bookings_count(mbo_client)
    if count > 0:
        return count
    return


def get_user_bookings_by_user_first_name(name, date_range):
    bookings = Booking.objects.get_user_bookings_by_user_first_name(name, date_range)
    return bookings


def cancel_bookings(bookings):
    for booking in bookings:
        update_client_visits(booking.mbo_visit_id, booking.slice_class.studio.mbo_site_id, 'cancel',
                             settings.MBO_STAFF_USERNAME,
                             settings.MBO_STAFF_PASSWORD)

        booking.cancel()
        user = booking.mbo_client.user
        logger.info("Cancelled the Test Booking for booking id {} first name {} last name {} email {}".format(booking.id, user.first_name, user.last_name, user.email))
