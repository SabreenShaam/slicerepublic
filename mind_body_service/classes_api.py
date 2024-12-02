from mind_body_online.ClassService import ClassServiceCalls
from django.core.exceptions import ValidationError
from mind_body_service.exceptions import UpdateClientVisitsException, AddClientToClassException, \
     NoAvailablePaymentException, MindBodyException
from slicerepublic.exceptions import InternalServerError

import logging

logger = logging.getLogger(__name__)


def get_classes(mbo_site_id, program_ids, start_date=None, end_date=None, page=0):
    class_service = ClassServiceCalls()
    class_list = class_service.GetClasses(
        mbo_site_ids=mbo_site_id,
        startDateTime=start_date,
        endDateTime=end_date,
        page=page,
        programIds=program_ids)
    return class_list


# todo : handle errors
def get_class(mbo_site_id, mbo_class_id, start_date=None, end_date=None, mbo_username=None, mbo_password=None):
    class_service = ClassServiceCalls()
    response = class_service.GetClasses(
        classIds=[mbo_class_id],
        startDateTime=start_date,
        endDateTime=end_date,
        mbo_site_ids=mbo_site_id,
        mbo_username=mbo_username,
        mbo_password=mbo_password)

    if response.Status != 'Success':
        logger.error("GetClasses service call failed (status : {})".format(response.Status))
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


# Todo : Improve this method
def add_client_to_class(mbo_client_id, mbo_site_id, mbo_class_id, mbo_username=None, mbo_password=None):

    class_service = ClassServiceCalls()
    response = class_service.AddClientsToClasses(
        [mbo_client_id],
        [mbo_class_id],
        site_ids=[mbo_site_id],
        mbo_username=mbo_username,
        mbo_password=mbo_password
    )

    if response.Status != 'Success':
        try:
            error_code = response.Classes.Class[0].Clients.Client[0].ErrorCode
            logger.debug("Error code : {}".format(error_code))
            if error_code == '603':
                message = "You are already booked at this time"
            elif error_code == '602':
                message = "You are Outside Scheduling Window"
            elif error_code == '601':
                message = "You have no available payments for this class"
            elif error_code == '600':
                message = "Registration for the class is full"
            else:
                message = None
                if hasattr(response, 'Message'):
                    message = response.Message
                    logger.error("Response status : {} Response Message: {}".format(response.Status, message))
                if hasattr(response.Classes.Class[0].Clients.Client[0], 'Messages'):
                    message = response.Classes.Class[0].Clients.Client[0].Messages[0][0].title()
                    logger.error("Response status : {} Response Message: {}".format(response.Status, message))
                if not message:
                     logger.error("Response status : {}".format(response.Status))

            if error_code == '601':
                raise NoAvailablePaymentException("80005", "Booking failed", message)

            raise AddClientToClassException("80001", "Booking failed", message)
        except Exception as ex:
            if isinstance(ex, AddClientToClassException):
                raise ex
            if isinstance(ex, NoAvailablePaymentException):
                raise ex
            logger.error(ex)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


# Todo : Improve this method
def get_class_visits(mbo_class_id, mbo_site_id, mbo_username=None, mbo_password=None):
    class_service = ClassServiceCalls()
    response = class_service.GetClassVisits(
        classId=mbo_class_id,
        mbo_site_ids=[mbo_site_id],
        mbo_username=mbo_username,
        mbo_password=mbo_password
    )

    if response.Status != 'Success':
        message = None
        try:
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if hasattr(response.Classes.Class[0].Clients.Client[0], 'Messages'):
                message = response.Classes.Class[0].Clients.Client[0].Messages[0][0].title()
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if not message:
                 logger.error("Response status : {}".format(response.Status))
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

        except Exception as ex:
            if isinstance(ex, InternalServerError):
                raise ex
            logger.error(ex)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


def remove_client_from_class(mbo_client_id, mbo_class_id, mbo_site_id):
    """
    Remove the client from the class.
    :return: response
    """
    class_service = ClassServiceCalls()
    response = class_service.RemoveClientFromClass(
        clientId=mbo_client_id,
        classId=mbo_class_id,
        siteId=mbo_site_id
    )

    if response.Status != 'Success':
        message = None
        try:
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if hasattr(response.Classes.Class[0].Clients.Client[0], 'Messages'):
                message = response.Classes.Class[0].Clients.Client[0].Messages[0][0].title()
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if not message:
                logger.error("Response status : {}".format(response.Status))

            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
        except Exception as ex:
            if isinstance(ex, ValidationError):
                raise ex
            logger.error(message)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def update_client_visits(mbo_visit_id, mbo_site_id, action, staff_username=None, staff_password=None):
    """
    Update client visits
    :return: response
    """
    visits = [{"ID": mbo_visit_id, "Execute": action}]
    class_service = ClassServiceCalls()
    response = class_service.UpdateClientVisits(
        visits=visits,
        site_id=mbo_site_id,
        mbo_username=staff_username,
        mbo_password=staff_password
    )

    if response.Status != 'Success':
        message = None
        try:
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if hasattr(response.Visits.Visit[0], 'Messages'):
                message = response.Visits.Visit[0].Messages[0][0].title()
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
                raise MindBodyException("80002", "Cancellation failed", message)
            if not message:
                 logger.error("Response status : {}".format(response.Status))

            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
        except Exception as ex:
            if isinstance(ex, MindBodyException):
                raise ex
            logger.error(ex)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def client_sign_in(mbo_visit_id, mbo_site_id, signed_in, staff_username=None, staff_password=None):
    """
    Sign in client.
    :return: response
    """
    visits = [{"ID": mbo_visit_id, "SignedIn": signed_in}]
    class_service = ClassServiceCalls()
    response = class_service.UpdateClientVisits(
        visits=visits,
        site_id=mbo_site_id,
        mbo_username=staff_username,
        mbo_password=staff_password
    )

    if response.Status != 'Success':
        message = None
        try:
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            if hasattr(response.Visits.Visit[0], 'Messages'):
                message = response.Visits.Visit[0].Messages[0][0].title()
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
                raise MindBodyException("80003", "Sign in failed", message)
            if not message:
                logger.error("Response status : {}".format(response.Status))

            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
        except Exception as ex:
            if isinstance(ex, MindBodyException):
                raise ex
            logger.error(ex)
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def get_class_schedules(start_date, end_date, mbo_site_id, mbo_program_ids, page=0):
    class_service = ClassServiceCalls()
    response = class_service.GetClassSchedules(
        programIds=mbo_program_ids,
        mbo_site_ids=[mbo_site_id],
        startDate=start_date.date(),
        endDate=end_date.date(),
        page=page,
    )
    if response.Status != 'Success':
        message = response.ClassSchedules.ClassSchedule[0].title()
        logger.error("Response status : {} Response Message: {}".format(response.Status, message))
        raise InternalServerError("10100", "Internal Error", message)

    return response
