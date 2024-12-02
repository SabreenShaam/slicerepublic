from celery.app import shared_task

from accounts.models import MboClientSettings, MboClient
from bookings.bookings_core.models import Booking
from fcm.FCMClient import FCMClient
from slicerepublic import dateutil
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_upcoming_booking_reminder(booking_id, mbo_client_id):
    mbo_client = MboClient.objects.get(id=mbo_client_id)
    if mbo_client:
        mbo_client_setting = MboClientSettings.objects.get_mbo_client_settings(mbo_client_id)
        logger.info("Upcoming remainder sending to Booking id {} mbo client {}".format(booking_id, mbo_client_id))
        start_dt = dateutil.get_local_datetime(dateutil.utcnow_plus(timedelta(days=-5)), "Europe/London")
        end_dt = dateutil.get_local_datetime(dateutil.utcnow_plus(timedelta(days=5)), "Europe/London")
        from bookings.bookings_core.booking_manager import sync_client_visits
        sync_client_visits(mbo_client, start_dt.date(), end_dt.date())

        booking = Booking.objects.get_booking_by_id(booking_id)
        if booking:
            if mbo_client_setting and not booking.is_cancelled and not booking.late_cancelled:
                if mbo_client_setting.remind_classes:
                    message_body = booking.slice_class.name + ' will start in 2 hours'
                    message_title = 'Fitopia'
                    data_message = {
                        "type": "1002",
                        "class_id": booking.slice_class.id,
                        "attended": booking.signed_in,
                    }
                    # TODO : badge should send and store notification
                    FCMClient.send_notification_to_mbo_client(mbo_client_id, data_message, message_body, message_title)
                    logger.info("Upcoming remainder has been Sent")
        else:
            logger.info("System couldn't find the booking record")
