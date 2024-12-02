from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class SliceClassDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN
