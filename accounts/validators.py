from accounts.accounts_manager import login, save_user_device_details
from accounts.models import CustomToken

import logging


class UserValidator(object):
    logger = logging.getLogger(__name__)

    def __init__(self, username, password, studio_id):
        self.username = username
        self.password = password
        self.studio_id = studio_id

    def __call__(self, *args, **kwargs):
        user = login(self.username,  self.password, self.studio_id)
        self.user = user
        return user

    def get_or_create_token(self, user):
        token = CustomToken.objects.get_or_create(user=user, studio_id=self.studio_id)
        self.logger.info("Token created for {}, token : {}".format(user.email, token[0].key))
        return token

    def track_device_information(self, device_info):
        save_user_device_details(self.user, device_info)
