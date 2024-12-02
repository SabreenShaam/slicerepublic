import json
from unittest import TestCase, skipIf

import django
from pyfcm.fcm import FCMNotification
from accounts.models import MboClient
from fcm.FCMClient import FCMClient
#from ratings.tasks import send_rating_notification
from notifications.models import Notification
from notifications.notification_manager import NotifyManager


class FCMClientTestCase(TestCase):
    def setUp(self):
        django.setup()

    @skipIf(False, "Skip this test")
    def test_push(self):
        data_message = {
            "heading": 'test heading',
            "body": 'test body',
            "type": "1001",
            "payload": {"class_id": 10250}
        }

        FCMClient.send_notification_to_mbo_client(1, "message", "message_body", "message_title")


    @skipIf(False, "Skip this test")
    def test_send_bulk_message(self):
        push_service = FCMNotification(api_key="AIzaSyCZZBYVsJmJWUymnzhmi0N87mNDVe9ifbc")
        registration_id = "<device registration_id>"
        registration_id="c4B_UTtzub0:APA91bEpeucBkR_OOE1JDfF_tyP69OjtNFZusfb_hIf2so2U3lO-GidaJVxAOyRrs5qwtjwKjdC116xHYS9Zp1ZeLuGGcGPwWpkLlXJreYi1oa1fgW9Ba_lUcDPCMN8KpqkOoGQc3gpA"
        #registration_id = "c0Bmt1RumJo:APA91bHh_-eTAgYZofyMcvSYZIWtiMDymMz2rQbS5jBgg8wsgkrRqoCItVET1cr7f-y7avB20tMfpxTOMdoR4_wlTT6XSXdK5HccZiuwx1ESwnaHGpirsifbE5a5UPyNZOqkARG2OJQ9"
        #result =push_service.notify_single_device(registration_id=registration_id, message_title="Alert", message_body="Chamika is greedy person")
        #message = "Hope you're having fun this weekend, don't forget to check today's news"
        # result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
        data = {}
        data['class_id'] = 129
        json_data = json.dumps(data)

        # data_message = {
        #     "heading": 'Fitopia123',
        #     "body": 'Please rate the class XXXXXXXXX',
        #     "type": "1001",
        #     "class_id": 2,
        #     "attended": 0,
        # }
        #
        data_message = {
            "type": "1001",
            "class_id": 129,
            "attended": True,
            "notification_id": 1,
        }

        # data_message = json.dumps(data_message)
        # aps = { "alert" : 'check aps'}

        message_title = "Fitopia123"
        message_body = 'this is message body'
        # To a single device

        notification = Notification(type="1001", message=str(data_message), mbo_client_id=1)
        notification.save()
        data_message.setdefault("id", notification.id)
        print('test')
        mbo_client = MboClient.objects.get(id=1)
        badge = len(NotifyManager.get_notifications(mbo_client.id, False))
        print(badge)
        result = push_service.notify_single_device(registration_id=registration_id,
                                                  data_message=data_message,  message_body=message_body, message_title=message_title, badge=1)

        # result = push_service.notify_single_device(registration_id=registration_id,
        #                                            data_message=data_message)


        # result = push_service.notify_multiple_devices(registration_ids=[registration_id],
        #                                            data_message=data_message)

        print(result)  # NotificationManager.send_notification("Sample Message from Fitopia")

    @skipIf(False, "Skip this test")
    def test_send_rating_notification(self):
        mbo_client = MboClient.objects.get(id=1)
        pass
        #send_upcoming_booking_reminder(1,1)
        #send_rating_notification(1, 1)

