from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class CreditCardNumberAuthorizationException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class CreditCardCommonException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class ForbiddenException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN
