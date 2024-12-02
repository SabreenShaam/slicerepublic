from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class StudioDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class StudioIdRequiredException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST

