from mind_body_online.StaffService import StaffServiceCalls
import logging


logger = logging.getLogger(__name__)


def validate_staff(username, password, mbo_site_id):
    staff_service_calls = StaffServiceCalls()
    result = staff_service_calls.VaildateStaff(
        username=username,
        password=password,
        mbo_site_ids=[mbo_site_id],)

    if result.Status != 'Success':
        message = None
        if hasattr(result, 'Message'):
            message = result.Message
            logger.error("Response status : {} Response Message: {}".format(result.Status, message))
        if not message:
            logger.error("Response status : {}".format(result.Status))

    return result
