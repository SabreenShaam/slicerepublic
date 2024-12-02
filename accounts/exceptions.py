from slicerepublic.exceptions import BaseSliceRepublicException
from rest_framework import status


class InvalidLoginException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class UserNameRequiredException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class PasswordRequiredException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class AppVersionDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_404_NOT_FOUND


class MemberAgreementRequiredException(BaseSliceRepublicException):
    status_code = status.HTTP_400_BAD_REQUEST


class MembershipRequiredException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class MissingParameterException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN


class UserDoesNotExistException(BaseSliceRepublicException):
    status_code = status.HTTP_404_NOT_FOUND


class UnAuthorizedException(BaseSliceRepublicException):
    status_code = status.HTTP_401_UNAUTHORIZED


class StudioAccessDoesNotExist(BaseSliceRepublicException):
    status_code = status.HTTP_404_NOT_FOUND


class SignupFailedException(BaseSliceRepublicException):
    status_code = status.HTTP_403_FORBIDDEN
