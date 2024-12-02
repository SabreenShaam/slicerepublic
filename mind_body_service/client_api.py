from mind_body_online.ClientService import ClientServiceCalls
from accounts.exceptions import InvalidLoginException, SignupFailedException
from slicerepublic.exceptions import InternalServerError

import logging

logger = logging.getLogger(__name__)


def validate_mbo_client_login(username, password, mbo_site_id):
    client_service = ClientServiceCalls()
    result = client_service.ValidateLogin(
        username=username,
        password=password,
        mbo_site_ids=[mbo_site_id],
    )

    if result.Status == "InvalidParameters":
        message = None
        if hasattr(result, 'Message'):
            message = result.Message
            logger.error("Response status : {} Response Message: {}".format(result.Status, message))
            raise InvalidLoginException("80004", "Login failed", message)
        if not message:
            logger.error("Response status : {}".format(result.Status))
            raise InvalidLoginException("80004", "Login failed", "Login failed")

    elif result.Status != "Success":
        if hasattr(result, 'Message'):
            message = result.Message
            logger.error("Response status : {} Response Message: {}".format(result.Status, message))
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return result.Client


def get_client_visits(staff_username, staff_password, mbo_client_id, start_date, end_date, mbo_site_id):
    client_service = ClientServiceCalls()
    response = client_service.GetClientVisits(
        clientId=mbo_client_id,
        startDate=start_date,
        endDate=end_date,
        mbo_site_ids=[mbo_site_id],
        mbo_username=staff_username,
        mbo_password=staff_password
    )

    if response.ErrorCode == '301':
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response Code : {} Response Message: {}".format(response.ErrorCode, message))
        if not message:
            logger.error("Response status : {}".format(response.Status))

        raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    elif response.Status != "Success":
        message = response.Message
        logger.error("Response status : {} Response Message: {}".format(response.Status, message))
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


def add_client(clients, mbo_site_id, mbo_username=None, mbo_password=None):

    client_service = ClientServiceCalls()
    response = client_service.AddOrUpdateClients(
        updateAction="AddNew",
        clients=clients,
        mbo_site_ids=[mbo_site_id],
        mbo_username=mbo_username,
        mbo_password=mbo_password
    )

    if response.Status != "Success":
        if hasattr(response, 'Message'):
            logger.error("Response status : {} Response Message: {}".format(response.Status, response.Message))

        if hasattr(response.Clients.Client[0], 'ErrorCode'):
            if response.Clients.Client[0].ErrorCode == '305':
                raise SignupFailedException("10100", "SignUp failed action", "Internal Service Error")

        message = None
        if hasattr(response.Clients.Client[0], 'Messages'):
            message = response.Clients.Client[0].Messages[0][0]
            logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            raise InternalServerError("10100", "Internal Error", message)

        if message is None:
            logger.error("Response status : {}".format(response.Status))
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def get_client_services(mbo_client_id, mbo_program_ids, mbo_site_id, start_date, end_date, show_active_only=False):
    client_service = ClientServiceCalls()
    response = client_service.GetClientServices(
        clientId=mbo_client_id,
        programIds=mbo_program_ids,
        mbo_site_ids=[mbo_site_id],
        startDate=start_date,
        endDate=end_date,
        showActiveOnly=show_active_only,
    )

    if response.Status != "Success":
        message = None
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response status : {} Response Message: {}".format(response.Status, message))
            raise InternalServerError("10100", "Internal Error", message)

        if not message:
            logger.error("Response status : {}".format(response.Status))
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def get_client(client_id, site_id):
    client_service = ClientServiceCalls()
    response = client_service.GetClientsByMultipleIds(ids=[client_id], mbo_site_ids=[site_id], field="Clients.ClientCreditCard")

    if response.Status != "Success":
        logger.error("Response status : {} Error code : {}".format(response.Status, response.ErrorCode))
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def get_required_client_fields(mbo_site_id):
    client_service = ClientServiceCalls()
    response = client_service.GetRequiredClientFields(
        site_ids=[mbo_site_id]
    )

    if response.Status != "Success":
            logger.error("Response status : {}".format(response.Status))
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def send_new_password_link_to_user_email(user_email, first_name, last_name, mbo_site_id):
    client_service = ClientServiceCalls()
    response = client_service.SendUserNewPassword(
        user_email=user_email,
        first_name=first_name,
        last_name=last_name,
        mbo_site_ids=[mbo_site_id]
    )

    if response.Status != "Success":
        message = None
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response status : {}".format(message))
            raise InternalServerError("10100", "Internal Error", message)

        if not message:
            logger.error("Response status : {}".format(response.Status))
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


def get_client_by_email(searchStr, mbo_username, mbo_password, mbo_site_id):
    client_service = ClientServiceCalls()
    response = client_service.GetClientsByString(
        searchStr=searchStr,
        mbo_username=mbo_username,
        mbo_password=mbo_password,
        mbo_site_ids=[mbo_site_id]
    )

    if response.Status != "Success":
        logger.error("Response status : {}".format(response.Status))

    return response
