import logging
from django.conf import settings
from classes.models import SliceClass
from mind_body_service.classes_api import get_class_visits


class FClassVisits(object):
    logger = logging.getLogger(__name__)

    def __init__(self, class_id):
        self.class_id = class_id
        self.MboVisits = self._fetch()

    def _fetch(self):
        slice_class = SliceClass.objects.get_class_by_id(self.class_id)
        response = get_class_visits(slice_class.mbo_class_id, slice_class.studio.mbo_site_id, settings.MBO_STAFF_USERNAME, settings.MBO_STAFF_PASSWORD)
        return response

    def get_class_visits(self):
        self.logger.info("Populating class visit info for class id {}".format(self.class_id))
        visits = self.populate_visit_info()

        return visits

    def populate_visit_info(self):
        visit_info = {}
        if self.MboVisits:
            attendees = []
            if self.MboVisits.Class.Visits:
                for visit in self.MboVisits.Class.Visits.Visit:
                    client_name = {}
                    client = visit.Client
                    client_name['first_name'] = client.FirstName
                    client_name['last_name'] = client.LastName

                    attendees.append(client_name)

            visit_info['visits'] = attendees
            visit_info['total_slots'] = self.MboVisits.Class.MaxCapacity
            visit_info['booked_slots'] = self.MboVisits.Class.TotalBooked

        return visit_info
