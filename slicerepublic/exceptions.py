from rest_framework.exceptions import APIException
from rest_framework import status


class BaseSliceRepublicException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, code, short_message, long_message):
        self.detail = {'code': code, 'short_message': short_message, 'long_message': long_message}


class InternalServerError(BaseSliceRepublicException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class InvalidParameterException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class ParseError(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class ValidationError(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST
