import logging
from accounts.models import MboClient
from fcm.FCMNotificationAPI import FCMNotificationAPI
from fcm.models import FCMInstance
from notifications.models import Notification


class FCMClient(object):
    logger = logging.getLogger(__name__)

    def __init__(self, request, data):
        self.mbo_client = self._fetch_mbo_client(request.user, request.auth.studio)
        self.instance_id = data.__getitem__('instance_id')

    def _fetch_mbo_client(self, user, studio):
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)
        return mbo_client

    def save(self):
        FCMInstance.objects.get_or_create(mbo_client=self.mbo_client, instance_id=self.instance_id)
        self.logger.info("FCM Instance created for mbo client {}".format(self.mbo_client.id))

    @staticmethod
    def send_notification_to_all(message, message_body, message_title):
        fcm_api = FCMNotificationAPI()
        fcm_instances = FCMInstance.objects.all()
        for instance in fcm_instances:
            response = fcm_api.notify_single_device(instance.instance_id, message, message_body, message_title)
            if 'failure' in response:
                if response['failure'] == 1:
                    instance.delete()

    @staticmethod
    def send_notification_to_mbo_client(mbo_client_id, message, message_body, message_title, badge=None):
        logger = logging.getLogger(__name__)

        is_success = False
        fcm_api = FCMNotificationAPI()
        fcm_instances = FCMInstance.objects.filter(mbo_client_id=mbo_client_id)
        for instance in fcm_instances:
            logger.debug("Notification sending to fcm instance {}".format(instance.id))
            response = fcm_api.notify_single_device(instance.instance_id, message, message_body, message_title, badge)
            if 'failure' in response:
                if response['failure'] == 1 and response['results'] and response['results'][0]['error']:
                    logger.error("Failed to sent the notification to mbo client id {} and reason {}".format(mbo_client_id, response['results'][0]['error']))
                    if response['results'][0]['error'] == "NotRegistered":
                        instance.delete()

            if 'success' in response and response['success'] == 1:
                is_success = True
                logger.debug("Notification successfully sent to fcm instance {}".format(instance.id))

        if not is_success:
            notification = Notification.objects.filter(id=message["notification_id"]).first()
            notification.mark_as_failure()
            logger.debug("Notification {} has been marked as failed".format(notification.id))

