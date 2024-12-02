from django.db import models
from accounts.models import MboClient


class FCMInstanceManager(models.Manager):
    def get_all_fcm_instances_for_mbo_client(self, mbo_client_id):
        query = self.filter(mbo_client_id=mbo_client_id)
        return query


class FCMInstance(models.Model):
    mbo_client = models.ForeignKey(MboClient)
    instance_id = models.CharField(max_length=255)

    objects = FCMInstanceManager()
