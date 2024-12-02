from django.db import models
from accounts.models import MboClient
import ast


class NotificationManager(models.Manager):
    def get_notifications(self, mbo_client_id, is_handled=None):
        query = self.filter(mbo_client_id=mbo_client_id)
        if is_handled is not None:
            query = query.filter(is_handled=is_handled)
        return query


class Notification(models.Model):
    type = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    is_handled = models.BooleanField(default=False)
    mbo_client = models.ForeignKey(MboClient, null=True)
    is_success = models.BooleanField(default=True)

    objects = NotificationManager()

    def mark_as_handled(self):
        self.is_handled = True
        self.save()

    def mark_as_failure(self):
        self.is_success = False
        self.save()

    @staticmethod
    def serialize(notifications):
        data = []
        for item in notifications:
            notification = {}
            notification['id'] = item.id
            notification['type'] = item.type
            notification['message'] = ast.literal_eval(item.message)
            notification['is_handled'] = item.is_handled
            data.append(notification)
        return data

