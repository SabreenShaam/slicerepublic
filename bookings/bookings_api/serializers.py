from rest_framework.serializers import ModelSerializer
from bookings.bookings_core.models import Booking
from classes.serializers import ClassSerializer


class BookingSerializer(ModelSerializer):
    slice_class = ClassSerializer()

    class Meta:
        model = Booking
        depth = 1
        exclude = ('mbo_visit_id', 'modified', 'created', 'mbo_client')
