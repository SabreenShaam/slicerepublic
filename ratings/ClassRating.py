from classes.models import SliceClass
from ratings.models import Rating
from ratings.tasks import send_rating_notification

from datetime import datetime

import logging
from slicerepublic import dateutil


class ClassRating(object):
    logger = logging.getLogger(__name__)

    def __init__(self, slice_class_id, mbo_client):
        self.rating = Rating.objects.get_rating_by_class_and_mbo_client(slice_class_id, mbo_client)
        self.slice_class_id = slice_class_id
        self.mbo_client = mbo_client

    def rate(self, value):
        if self.rating:
            self.rating.update(value)
            self.logger.info(
                "Rating updated (rating_id : {}, slice_class_id : {}, mbo_client_id {})".format(self.rating.id,
                                                                                                self.rating.slice_class.id,
                                                                                                self.rating.mbo_client.id))
        else:
            # todo: validate class
            rating = Rating.objects.create(slice_class_id=self.slice_class_id, mbo_client=self.mbo_client, value=value)
            self.logger.info(
                "Rating created (rating_id : {}, slice_class_id : {}, mbo_client_id {})".format(rating.id,
                                                                                                rating.slice_class.id,
                                                                                                rating.mbo_client.id))

    def get_rating(self):
        return self.populate_rating()

    @staticmethod
    def schedule_rating_notification(mbo_client_id, booking_id, slice_class):
        end_date = slice_class.end_date
        end_time = slice_class.end_time
        scheduled_dt = datetime(end_date.year, end_date.month, end_date.day, end_time.hour, end_time.minute)
        localized_time = dateutil.localize(scheduled_dt)

        send_rating_notification.apply_async((booking_id, mbo_client_id), eta=localized_time)

    def populate_rating(self):
        slice_class = SliceClass.objects.get_class_by_id(self.slice_class_id)
        response = {}
        response['value'] = 0
        value = Rating.objects.get_rating_by_schedule(slice_class.schedule.id)
        count = Rating.objects.get_rating_count_by_schedule(slice_class.schedule.id)
        if value['value__avg']:
            response['value'] = round(value['value__avg'], 1)
            response['count'] = count
            return response
        return response
