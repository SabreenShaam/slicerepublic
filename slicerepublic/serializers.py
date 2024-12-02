from rest_framework import serializers


class GeneralModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def __init__(self, instance):
        self.Meta.model = type(instance)
        super(GeneralModelSerializer, self).__init__(instance=instance)
