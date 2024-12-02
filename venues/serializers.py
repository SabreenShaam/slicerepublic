from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from venues.models import Location, Studio, MBOLocation, StudioPricing


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'city')


class LocationAllSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'latitude', 'longitude')


class MBOLocationSerializer(ModelSerializer):
    location = LocationAllSerializer()

    class Meta:
        model = MBOLocation
        fields = ('id', 'location')


class StudioSerializer(ModelSerializer):
    locations = MBOLocationSerializer(many=True)

    class Meta:
        model = Studio
        # exclude = ('mbo_site_id',)


class StudioBasicSerializer(ModelSerializer):
    class Meta:
        model = Studio
        fields = ('id', 'name')


class PriceSerializer(ModelSerializer):
    class Meta:
        model = StudioPricing
        fields = ('price')


class StudioPricingSerializer(ModelSerializer):
    studio = StudioBasicSerializer()

    class Meta:
        model = StudioPricing
        fields = ('id', 'studio', 'drop_in_price', 'ten_pack_price', 'drop_in_transfer_price', 'ten_pack_transfer_price', 'transfer_price')
