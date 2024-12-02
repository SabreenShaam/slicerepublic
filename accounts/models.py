from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
from model_utils.models import TimeStampedModel

from slicerepublic import dateutil
from venues.models import Studio
from datetime import timedelta
import binascii
import os

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class CustomToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(AUTH_USER_MODEL)
    studio = models.ForeignKey(Studio)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authtoken_token'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(CustomToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_active, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, is_active=True, **extra_fields):
        return self._create_user(email, password, is_active, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def get_count_by_email(self, email):
        return self.filter(email=email).count()

    def get_user_by_email_and_verification_hash(self, email, verification_hash):
        return self.filter(email=email, verification_hash=verification_hash).first()

    def get_user_by_email(self, email):
        return self.filter(email=email).first()

    def search_user(self, email, studio_id):
        query = self.filter(mbo_client__studio_id=studio_id, email=email).first()
        return query


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    A User of the system
    """
    first_name = models.CharField('first name', max_length=30)
    last_name = models.CharField('last name', max_length=30)
    email = models.EmailField('email address', blank=False, null=False, unique=True)
    is_active = models.BooleanField('active', default=True)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    mobile_phone = models.CharField(max_length=12)
    verification_hash = models.CharField(max_length=32, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_username(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return self.email


class MboClientManager(models.Manager):
    def get_mbo_client_by_user_preload_studio(self, user):
        query = self.select_related('studio').get(user=user)
        return query

    def get_mbo_client_by_studio_and_user(self, user, studio):
        return self.filter(user=user, studio=studio).select_related('studio').first()

    def get_users_info_list(self,  start, end, email=None, first_name=None, last_name=None, studio=None):
        filters = {'user__email__icontains': email, 'user__first_name__icontains': first_name, 'user__last_name__icontains': last_name, 'created__range': [start, end], 'studio__name__icontains': studio}
        arguments = {}
        for k, v in filters.items():
            if v:
                arguments[k] = v
        query = self.select_related('user').filter(**arguments)

        return query

    def search(self, page, **kwargs):
        query = self.__get_search_query(**kwargs).order_by('-created')
        if page:
            start = (page - 1) * settings.SEARCH_PAGE_LIMIT
            end = start + settings.SEARCH_PAGE_LIMIT
            query = query[start:end]
        else:
            query = query[:settings.SEARCH_PAGE_LIMIT]

        return query

    def count(self, **kwargs):
        query = self.__get_search_query(**kwargs)
        return query.count()

    def __get_search_query(self, **kwargs):
        filters = {
            'email': 'user__email__icontains',
            'first_name': 'user__first_name__icontains',
            'last_name': 'user__last_name__icontains',
            'studio': 'studio__name__icontains',
        }

        arguments = {}
        for key, value in kwargs.items():
            arguments[filters[key]] = value

        if 'start_date' not in kwargs:
            start_date = dateutil.utc_today_midnight_plus(timedelta(days=-365))

        if 'end_date' not in kwargs:
            end_date = dateutil.utc_today_midnight_plus(timedelta(days=1))

        arguments['created__range'] = [start_date, end_date]

        query = self.select_related('user').filter(**arguments)
        return query


class MboClient(TimeStampedModel):
    user = models.ForeignKey(User, related_name='mbo_client')
    mbo_client_id = models.CharField(max_length=50)
    studio = models.ForeignKey(Studio)
    unique_id = models.CharField(max_length=50, null=True)

    objects = MboClientManager()

    def is_home_studio(self, studio):
        if self.studio == studio:
            return True
        return False

    def update(self, client_id):
        self.mbo_client_id = client_id
        self.save()

    @staticmethod
    def get_results(mbo_users):
        result = []
        for mbo_user in mbo_users:
            user_info = {}
            user_info['email'] = mbo_user.user.email
            user_info['first_name'] = mbo_user.user.first_name
            user_info['last_name'] = mbo_user.user.last_name
            user_info['home_studio'] = mbo_user.studio.name
            result.append(user_info)
        return result


class StaffManager(models.Manager):
    def get_staff_by_user_id(self, user_id):
        return self.filter(user_id=user_id).first()


class Staff(models.Model):
    user = models.OneToOneField(User, related_name='staff')
    studio = models.ForeignKey(Studio)

    objects = StaffManager()


class MemberSettingsManager(models.Manager):
    def get_member_settings_by_user(self, user):
        query = self.filter(user=user).first()
        return query


class MemberSettings(models.Model):
    user = models.OneToOneField(User, related_name='member_settings')
    is_liability_accepted = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=True)
    email_remainder = models.BooleanField(default=True)

    objects = MemberSettingsManager()


class AppVersionManager(models.Manager):
    def get_app_version_by_platform(self, platform):
        query = self.filter(platform=platform).first()
        return query


class AppVersion(models.Model):
    platform = models.CharField(max_length=15)
    version = models.CharField(max_length=15)
    enabled = models.BooleanField(default=True)
    objects = AppVersionManager()


class UserDeviceManager(models.Manager):

    def get_last_login_by_user_id(self, user):
        last_login_record = self.filter(user=user).last()
        return last_login_record.login_time

    def get_user_last_device_by_user_id(self, user):
        last_device_record = self.filter(user=user).last()
        return last_device_record.device


class UserDevice(models.Model):
    user = models.ForeignKey(User, related_name='user_device')
    login_time = models.DateTimeField()
    device_type = models.CharField(max_length=200, null=True)
    app_version = models.CharField(max_length=200, null=True)
    os_version = models.CharField(max_length=200, null=True)
    device_scale = models.CharField(max_length=200, null=True)

    objects = UserDeviceManager()


class MboExternalClientManager(models.Manager):
    def get_mbo_external_client_by_user(self, user):
        query = self.filter(user=user).first()
        return query


class MboExternalClient(models.Model):
    user = models.ForeignKey(User)
    mbo_client_id = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    objects = MboExternalClientManager()


class UserExternalStudioManager(models.Manager):
    def get_user_external_studio_by_user_and_studio(self, user, studio):
        query = self.filter(user=user, studio=studio).first()
        return query


class UserExternalStudio(models.Model):
    user = models.ForeignKey(User)
    studio = models.ForeignKey(Studio)

    objects = UserExternalStudioManager()


class SignUpUsers(TimeStampedModel):
    mbo_client = models.ForeignKey(MboClient)


class MboClientSettingsManager(models.Manager):
    def get_mbo_client_settings(self, mbo_client_id):
        query = self.filter(mbo_client_id=mbo_client_id).first()
        return query


class MboClientSettings(models.Model):
    mbo_client = models.ForeignKey(MboClient, null=True)
    remind_classes = models.BooleanField(default=True)

    objects = MboClientSettingsManager()

    def update(self, is_enable):
        self.remind_classes = is_enable
        self.save()
