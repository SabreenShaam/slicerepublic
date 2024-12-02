from rest_framework.serializers import ModelSerializer
from ratings.models import Rating


class RateSerializer(ModelSerializer):
    class Meta:
        model = Rating
        exclude = ('id', 'slice_class', 'mbo_client')
