from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class UpdateClientVisitsException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class AddClientToClassException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class NoAvailablePaymentException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class MindBodyException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN
