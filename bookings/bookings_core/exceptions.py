from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class ClassFullException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class ExternalBookingsExceededException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class ExternalLateCancelException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class LateCancelException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class OutsideOfBookingWindowException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class BookingDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN
