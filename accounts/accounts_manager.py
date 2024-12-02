from datetime import timedelta
import hashlib
from django.core.paginator import Paginator, EmptyPage
from accounts.exceptions import UserDoesNotExistException, SignupFailedException
from accounts.mbo_client_manager import MboClientManager, SignUpManager
from fcm.models import FCMInstance
from mind_body_service.client_api import validate_mbo_client_login, get_required_client_fields, add_client, \
    send_new_password_link_to_user_email
from slicerepublic.dateutil import utcnow_millis
from slicerepublic.sendmail import send_signup_notification_email_to_studio

from venues.models import Studio
from accounts.models import User, MboClient, MemberSettings, UserDevice, SignUpUsers

from slicerepublic.exceptions import InternalServerError
from venues.exceptions import StudioDoesNotExistException

from services.service_manager import client_services_sync
from slicerepublic import dateutil
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def login(email, password, studio_id):
    logger.info("Entered login (username : {}, studio_id : {})".format(email, studio_id))
    try:
        studio = Studio.objects.get_studio_by_studio_id(studio_id)
        mbo_site_id = studio.mbo_site_id
    except Studio.DoesNotExist:
        message = "Invalid studio id"
        logger.error(message)
        raise StudioDoesNotExistException("40000", message, "Login failed. Studio id is invalid.")

    client = validate_mbo_client_login(email, password, mbo_site_id)
    logger.info("{} is a valid mbo user".format(email))
    host_name = settings.SIGNUP_VERIFICATION_HOST_NAME
    user, mbo_client = mapping_mbo_client_with_user(host_name, email, client, studio, True)

    MboClientManager.update_client_info(client, mbo_client)

    client_services_sync(mbo_client)

    logger.info("Leaving login")

    return user


def populate_user(user, client):
    user.first_name = client.FirstName
    user.last_name = client.LastName
    if hasattr(client, 'MobilePhone'):
        user.mobile_phone = client.MobilePhone
    return user


def get_member_agreement_status(user):
    member_settings = MemberSettings.objects.get_member_settings_by_user(user)

    if not member_settings:
        logger.info(
            "Member settings not found. Hence member ({}) has not accepted liability agreement.".format(user.email))
        return False

    logger.info("Member agreement status {} for {}.".format(member_settings.is_liability_accepted, user.email))
    return member_settings.is_liability_accepted


def update_member_agreement_status(user, status):
    member_settings = MemberSettings.objects.get_member_settings_by_user(user)

    if status == 'false':
        status = False
    elif status == 'true':
        status = True

    if not member_settings:
        logger.info("No member settings found, creating one for {} - (status: {})".format(user.email, status))
        member_settings = MemberSettings()
        member_settings.user = user
        member_settings.is_liability_accepted = status
        member_settings.save()
    elif member_settings.is_liability_accepted != status:
        member_settings.is_liability_accepted = status
        member_settings.save()

    logger.info("Member agreement updated for {}.".format(user.email))


def save_user_device_details(user, device_info):
    try:
        device_type, app_version, os_version, device_scale = device_info.split(' ')
    except ValueError:
        message = "Error while saving device information"
        logger.error(message)
        return

    user_device = UserDevice()
    user_device.user = user
    user_device.login_time = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    user_device.device_type = device_type
    user_device.app_version = app_version
    user_device.os_version = os_version
    user_device.device_scale = device_scale
    user_device.save()


"""get last login of a user"""


def get_last_login_by_user_id(user):
    last_login = UserDevice.objects.get_last_login_by_user_id(user)
    return last_login


"""get last login device of the user"""


def get_user_last_device_by_user_id(user):
    last_login_device = UserDevice.objects.get_user_last_device_by_user_id(user)
    return last_login_device


def get_required_fields_by_studio_id(studio_id):
    try:
        studio = Studio.objects.get_studio_by_studio_id(studio_id)
    except Studio.DoesNotExist:
        message = "Invalid studio id"
        logger.debug(message)
        raise StudioDoesNotExistException("40000", "Studio does not exist", message)

    response = get_required_client_fields(studio.mbo_site_id)
    required_fields = []
    if response.RequiredClientFields:
        signup_manager = SignUpManager(None)
        required_fields = signup_manager._populate_required_fields(response.RequiredClientFields.string)

    if response.ResultCount == 0:
        signup_manager = SignUpManager(None)
        required_fields = signup_manager.populate_mandatory_required_fields()

    return required_fields


def signup_user_to_studio(client_info, studio):
    try:
        response = add_client(client_info, studio.mbo_site_id)
    except SignupFailedException:
        response = add_client(client_info, studio.mbo_site_id, settings.MBO_STAFF_USERNAME, settings.MBO_STAFF_PASSWORD)

    if hasattr(response.Clients, 'Client') and response.Clients:
        client = response.Clients.Client[0]
        host_name = settings.SIGNUP_VERIFICATION_HOST_NAME
        save_client_details(host_name, client, studio)


def save_client_details(host_name, client, studio):
    mapping_mbo_client_with_user(host_name, client.Email, client, studio, False)


def search_user(email, studio_id):
    logger.debug("Entered search user (email: {}, studio_id: {})".format(email, studio_id))
    user = User.objects.search_user(email, studio_id)
    logger.debug("Leaving search user")
    return user


def mapping_mbo_client_with_user(host_name, email, client, studio, from_login):
    hash_object = hashlib.md5(bytes(str(utcnow_millis()), encoding='utf-8'))
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create(email=email)
        user = populate_user(user, client)
        user.save()
    except User.MultipleObjectsReturned:
        message = "There are multiple users for the given username."
        logger.error(message)
        raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)

    if not mbo_client:
        mbo_client = MboClient.objects.create(user=user, mbo_client_id=client.ID, studio=studio,
                                              unique_id=client.UniqueID)
        if not from_login:
            SignUpUsers.objects.create(mbo_client=mbo_client)
            send_signup_notification_email_to_studio(host_name, email, studio.contact_email)

    return user, mbo_client


def get_verification_hash_for_user(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise UserDoesNotExistException("40050", "user not found", "User Does not exist")
    return user.verification_hash


def send_link_to_user_to_set_new_password(email, studio_id):
    try:
        user = User.objects.get(email=email)
        studio = Studio.objects.get_studio_by_studio_id(studio_id)
    except User.DoesNotExist:
        message = "User Does not exist"
        logger.debug(message)
        raise UserDoesNotExistException("40050", "user not found", message)
    except Studio.DoesNotExist:
        message = "Invalid studio id"
        logger.debug(message)
        raise StudioDoesNotExistException("40000", "Studio does not exist", message)

    result = send_new_password_link_to_user_email(email, user.first_name, user.last_name, studio.mbo_site_id)
    logger.info("Password link sent to {}.".format(email))
    return result


def clear_push_notification_instance(request, data):
    if "instance_id" in data:
        instance_id = data.__getitem__('instance_id')
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=request.user, studio=request.auth.studio)
        fcm_instance = FCMInstance.objects.filter(mbo_client=mbo_client, instance_id=instance_id)
        if fcm_instance:
            fcm_instance.delete()
            logger.debug("Push instance is deleted for mbo client {}".format(mbo_client.id))


class UserListManager(object):
    logger = logging.getLogger(__name__)

    def __init__(self, request, page_number):
        self.filters = {'email': None, 'first_name': None, 'last_name': None, 'start_date': dateutil.utcnow_plus(timedelta(days=-365)).date(), 'end_date': dateutil.utcnow_plus(timedelta(days=1)).date(), 'studio': None}
        self.request = request
        self.user_info_list = []
        self.page_number = page_number
        self.populate_filter_parameters()

    def populate_filter_parameters(self):
        for key, value in self.filters.items():
            if self.request.QUERY_PARAMS:
                if key in dict(self.request.QUERY_PARAMS):
                    self.filters[key] = self.request.QUERY_PARAMS[key]

    def get_users(self):
        logger.debug("Getting the users from {} to {}".format(self.filters['start_date'], self.filters['end_date']))
        mbo_user_list = MboClient.objects.get_users_info_list(self.filters['start_date'], self.filters['end_date'], email=self.filters['email'], first_name=self.filters['first_name'], last_name=self.filters['last_name'], studio=self.filters['studio'])
        for mbo_client_user in mbo_user_list:
            user_info = populate_user_info(mbo_client_user.user, mbo_client_user.studio)
            self.user_info_list.append(user_info)

        if self.page_number:
            return self.get_range_records()
        else:
            return self.user_info_list

    def get_range_records(self):
        try:
            paginator = Paginator(self.user_info_list, 100)
            page = paginator.page(self.page_number)
            return page.object_list
        except EmptyPage as e:
            self.user_info_list.clear()
            return self.user_info_list


def populate_user_info(mbo_user, home_studio):
    user_info = {}
    user_info['email'] = mbo_user.email
    user_info['first_name'] = mbo_user.first_name
    user_info['last_name'] = mbo_user.last_name
    user_info['home_studio'] = home_studio.name
    return user_info

