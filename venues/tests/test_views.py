from django.test import TestCase
from rest_framework import status
from model_mommy import mommy
import json


class StudioViewTestCase(TestCase):

    def test_studio_empty_list(self):
        response = self.client.get("/venues/api/studio")
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_studio_list(self):
        studio_one = mommy.make_recipe('venues.studio')
        studio_two = mommy.make_recipe('venues.studio', name='Slice', mbo_site_id=29730)

        response = self.client.get("/venues/api/studio")
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        content = json.loads(response.content.decode('utf-8'))
        self.assertEquals(2, len(content))