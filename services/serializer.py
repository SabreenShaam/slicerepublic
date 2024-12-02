from rest_framework.serializers import ModelSerializer
from services.models import MboClientService, StudioService, ClientCreditCardInfo, PassportStudioAccess
from venues.serializers import StudioBasicSerializer, PriceSerializer


class MboClientServiceSerializer(ModelSerializer):
    class Meta:
        model = MboClientService
        fields = ('id', 'name', 'count', 'remaining', 'expiration_date', 'auto_pay')


class StudioServiceSerializer(ModelSerializer):
    class Meta:
        model = StudioService
        fields = ('id', 'name', 'online_price', 'tax_rate', 'count',)


class ClientCreditCardSerializer(ModelSerializer):
    class Meta:
        model = ClientCreditCardInfo
        fields = ('id', 'type', 'last_four', 'exp_month', 'exp_year', 'postal_code')


class PassportStudioAccessSerializer(ModelSerializer):
    studio = StudioBasicSerializer()

    class Meta:
        model = PassportStudioAccess
        exclude = ('mbo_service',)
