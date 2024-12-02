from django.test import TestCase
from unittest import skipIf
from mind_body_service.classes_api import ClassServiceCalls


class ClassServiceTestCase(TestCase):

    def setUp(self):
        self.class_service = ClassServiceCalls()

    @skipIf(False, "Skip this test")
    def test_update_client_visits(self):
        visit_id = 100343777
        action = 'cancel'
        visits = [{"ID": visit_id, "Execute": action}]
        response = self.class_service.UpdateClientVisits(visits, -99, False, False)
        self.assertEquals(response.Status, 'Success')
