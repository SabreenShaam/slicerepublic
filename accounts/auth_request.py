from slicerepublic.exceptions import ParseError, ValidationError
from accounts.exceptions import UserNameRequiredException, PasswordRequiredException
from venues.exceptions import StudioIdRequiredException

import logging


class UserAuthRequest(object):
    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request

        try:
            self.data = request.DATA
        except ParseError as error:
            message = "Invalid Format - {0}".format(error.detail)
            self.logger.error(message)
            raise ParseError(40080, "Malformed request.", message)

    def validate(self):
        self.validate_username()
        self.validate_password()
        self.validate_studio()

    def validate_username(self):
        if "username" not in self.data:
            message = "username : Required parameter missing"
            self.logger.error(message)
            raise UserNameRequiredException("40010", "Missing Parameter", message)

    def validate_password(self):
        if "password" not in self.data:
            message = "password : Required parameter missing"
            self.logger.error(message)
            raise PasswordRequiredException("40020", "Missing Parameter", message)

    def validate_studio(self):
        if "studio_id" not in self.data:
            message = "studio_id : Required parameter missing"
            self.logger.error(message)
            raise StudioIdRequiredException("40030", "Missing Parameter", message)

        studio_id = self.data.__getitem__('studio_id')

        if not studio_id.isdigit():
            message = "Studio id value is invalid"
            self.logger.error(message)
            raise ValidationError("40031", "Invalid studio id", message)

    def get_data(self):
        username = self.data.__getitem__('username')
        password = self.data.__getitem__('password')
        studio_id = self.data.__getitem__('studio_id')
        self.logger.info("Entered token view (username : {}, studio id : {})".format(username, studio_id))
        return username, password, studio_id
