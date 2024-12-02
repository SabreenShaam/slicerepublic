from mind_body_service.classes_api import get_class, get_class_visits
from bookings.bookings_core.exceptions import ClassFullException

from django.conf import settings

from slicerepublic.exceptions import InternalServerError
import logging


class MboGetClass(object):
    logger = logging.getLogger(__name__)

    def __init__(self, site_id, class_id, start_date, end_date):
        self.site_id = site_id
        self.class_id = class_id
        self.start_date = start_date
        self.end_date = end_date
        self.response = self.__fetch()

    def __fetch(self):
        response = get_class(mbo_site_id=self.site_id,
                             mbo_class_id=self.class_id,
                             start_date=self.start_date,
                             end_date=self.end_date,
                             mbo_username=settings.MBO_STAFF_USERNAME,
                             mbo_password=settings.MBO_STAFF_PASSWORD)
        return response

    def get_class(self):
        return self.response.Classes[0][0]

    def is_empty(self):
        if not self.response or self.response.ResultCount == 0:
            message = "No class found in MBO instance (site_id : {}, class_id : {})".format(self.site_id, self.class_id)
            self.logger.error(message)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
        return True

    def get_site_id(self):
        return self.get_class().Location.SiteID

    def get_class_id(self):
        return self.get_class().ID

    def has_free_web_slot(self):
        self.logger.debug("Web capacity : {}, Web booked : {})".format(self.get_class().WebCapacity, self.get_class().WebBooked))
        if self.get_class().WebBooked >= self.get_class().WebCapacity:
            message = "Registration for the class is full."
            self.logger.error(message)
            raise ClassFullException("60030", "Class full", message)
        return True

    def has_free_slot(self):
        self.logger.debug("Max capacity : {}, Total booked : {})".format(self.get_class().MaxCapacity, self.get_class().TotalBooked))
        if self.get_class().TotalBooked >= self.get_class().MaxCapacity:
            message = "Registration for the class is full."
            self.logger.error(message)
            raise ClassFullException("60030", "Class full", message)
        return True


class MboGetClassVisit(object):
    logger = logging.getLogger(__name__)

    def __init__(self, site_id, class_id):
        self.site_id = site_id
        self.class_id = class_id
        self.response = self.__fetch()

    def __fetch(self):
        response = get_class_visits(self.class_id, self.site_id)
        return response

    def get_visit_for_given_client(self, mbo_client_id):
        for visit in self.response.Class.Visits.Visit:
            if visit.Client.ID == mbo_client_id:
                self.logger.info("Visit ({}) found for {}".format(visit.ID, mbo_client_id))
                return visit
        self.logger.error("No visits found in the class!")
        return None
