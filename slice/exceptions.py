from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class SliceClientDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class SliceServiceDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST
