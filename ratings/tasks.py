from celery.app import shared_task

from bookings.bookings_core.models import Booking
from fcm.FCMClient import FCMClient
import logging
from fcm.models import FCMInstance
from notifications.notification_manager import NotifyManager

logger = logging.getLogger(__name__)


@shared_task
def send_rating_notification(booking_id, mbo_client_id):
    logger.info("Rating notification sending to Booking id {} and mbo client {}".format(booking_id, mbo_client_id))
    booking = Booking.objects.get_booking_by_id(booking_id)
    if booking:
        if not booking.is_cancelled and not booking.late_cancelled:
            message_body = 'Please rate ' + booking.slice_class.name
            message_title = 'Fitopia'
            data_message = {
                "type": "1001",
                "class_id": booking.slice_class.id,
                "attended": booking.signed_in,
            }
            count = FCMInstance.objects.get_all_fcm_instances_for_mbo_client(mbo_client_id).count()
            if count > 0:
                notification = NotifyManager().track_sent_rating_notification(mbo_client_id, data_message)
                badge = len(NotifyManager.get_notifications(mbo_client_id, False))
                data_message['notification_id'] = notification.id

                FCMClient.send_notification_to_mbo_client(mbo_client_id, data_message, message_body, message_title, badge)
                logger.info("Rating Notification has been Sent")
            else:
                logger.debug("FCMInstances not exist for mbo client id {}".format(mbo_client_id))

    else:
        logger.info("System couldn't find the booking record")


@shared_task
def test_async_task(a, b):
    import logging
    from celery.utils.log import get_task_logger
    loggerp = logging.getLogger(__name__)
    loggert = get_task_logger(__name__)
    result = a + b
    print("Print Result: {}".format(result))
    loggerp.info("Python logger Result: {}".format(result))
    loggert.info("Task logger Result: {}".format(result))
