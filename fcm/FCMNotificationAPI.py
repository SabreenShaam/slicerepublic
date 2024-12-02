from django.conf import settings
from pyfcm import FCMNotification
from pyfcm.errors import FCMServerError, InternalPackageError

from slicerepublic.exceptions import InternalServerError

import logging


def get_notification_service():
    notification_service = FCMNotification(api_key=settings.FCM_API_KEY)
    return notification_service


class FCMNotificationAPI(object):
    logger = logging.getLogger(__name__)

    def notify_single_device(self, instance_id, data_message, message_body, message_title, badge=None):
        notification_service = get_notification_service()

        try:
            response = notification_service.notify_single_device(registration_id=instance_id,
                                                   data_message=data_message,  message_body=message_body, message_title=message_title, badge=badge)

        except InternalPackageError:
            message = "Raised InternalPackageError (registration_id : {}, data_message : {})".format(instance_id, data_message)
            self.__raise_internal_server_error_and_log_error_message(message)
        except FCMServerError:
            message = "Raised FCMServerError (registration_id : {}, data_message : {})".format(instance_id, data_message)
            self.__raise_internal_server_error_and_log_error_message(message)
        except Exception:
            message = "Unknown exception occurred (registration_id : {}, data_message : {})".format(instance_id, data_message)
            self.__raise_internal_server_error_and_log_error_message(message)

        return response

    def __raise_internal_server_error_and_log_error_message(self, message):
        self.logger.error(message)
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")




