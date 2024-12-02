from venues.models import Studio
from mind_body_service.staff_api import validate_staff
from accounts.exceptions import UnAuthorizedException

import logging


class StaffValidator(object):
    logger = logging.getLogger(__name__)

    def __init__(self, username, password, studio_id):
        self.username = username
        self.password = password
        self.studio_id = studio_id

    def __call__(self, *args, **kwargs):
        studio = Studio.objects.get_studio_by_studio_id(self.studio_id)
        response = validate_staff(self.username, self.password, studio.mbo_site_id)
        if response.Status != 'Success':
            message = response.Message
            self.logger.error(message)
            raise UnAuthorizedException("80004", "Staff validation failed", message)
        return
