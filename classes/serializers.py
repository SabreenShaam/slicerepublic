from rest_framework import serializers
from staff.serializers import StaffSerializer
from venues.serializers import StudioSerializer, LocationSerializer
from classes.models import SliceClass, SessionType


class SessionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionType
        fields = ('name',)


class ClassSerializer(serializers.ModelSerializer):
    staff = StaffSerializer()
    location = LocationSerializer()
    bookable = serializers.ReadOnlyField()
    studio = StudioSerializer()

    class Meta:
        model = SliceClass
        exclude = ('created', 'modified', 'mbo_last_updated', 'mbo_class_id', 'session_type', 'mbolocation')
        depth = 1
