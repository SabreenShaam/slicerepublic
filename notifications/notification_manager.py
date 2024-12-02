from notifications.models import Notification
import logging


class NotifyManager(object):
    logger = logging.getLogger(__name__)

    @staticmethod
    def get_notifications(mbo_client_id, is_handled):
        results = Notification.objects.get_notifications(mbo_client_id, is_handled)
        notifications = Notification.serialize(results)
        return notifications

    def update(self, id, is_handled):
        notification = Notification.objects.filter(id=id).first()
        if notification:
            if is_handled == "True":
                notification.mark_as_handled()
                self.logger.debug("Notification status updated for id={}".format(id))

    def track_sent_rating_notification(self, mbo_client_id, data_message):
        notification = Notification.objects.create(type='1001', mbo_client_id=mbo_client_id, message=str(data_message))
        self.logger.debug("Tracked sent rating notification (mbo_client_id: {}, notification_id:{})".format(mbo_client_id, notification.id))
        return notification
