from rest_framework.serializers import ModelSerializer, SerializerMethodField
from accounts.models import User, MboClient, AppVersion, MboClientSettings


class UserSerializer(ModelSerializer):
    home_studio = SerializerMethodField()

    class Meta:
        model = User
        exclude = ('date_joined',
                   'last_login',
                   'is_superuser',
                   'password',
                   'user_permissions',
                   'groups',
                   'verification_hash')

    def get_home_studio(self, obj):
        home_studio = self.context.get("home_studio")
        return home_studio.name


class AppVersionSerializer(ModelSerializer):
    class Meta:
        model = AppVersion
        exclude = ('id',)


class MboClientSettingSerializer(ModelSerializer):
    class Meta:
        model = MboClientSettings
        exclude = ('id', 'mbo_client',)

