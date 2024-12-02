from django.db import models
from django.db.models.aggregates import Avg
from accounts.models import MboClient
from classes.models import SliceClass


class RatingManager(models.Manager):
    def get_rating_by_class_and_mbo_client(self, slice_class_id, mbo_client_id):
        return self.select_related('slice_class', 'mbo_client').filter(slice_class_id=slice_class_id, mbo_client_id=mbo_client_id).first()

    def get_rating_by_schedule(self, schedule_id):
        query = self.filter(slice_class__schedule_id=schedule_id).aggregate(Avg('value'))
        return query

    def get_rating_count_by_schedule(self, schedule_id):
        query = self.filter(slice_class__schedule_id=schedule_id).count()
        return query


class Rating(models.Model):
    value = models.PositiveIntegerField()
    slice_class = models.ForeignKey(SliceClass, null=True)
    mbo_client = models.ForeignKey(MboClient, null=True)

    objects = RatingManager()

    def update(self, value):
        self.value = value
        self.save()
