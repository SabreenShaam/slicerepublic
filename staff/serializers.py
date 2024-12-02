from rest_framework.serializers import ModelSerializer
from .models import Staff


class StaffSerializer(ModelSerializer):
    class Meta:
        model = Staff
        fields = ('id', 'first_name', 'last_name', 'name')