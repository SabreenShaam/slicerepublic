from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated

from accounts.accounts_manager import get_member_agreement_status, update_member_agreement_status, \
    get_required_fields_by_studio_id, signup_user_to_studio, save_client_details, search_user, \
    get_verification_hash_for_user, send_link_to_user_to_set_new_password, clear_push_notification_instance
from accounts.authentication import CustomTokenAuthentication

from accounts.exceptions import AppVersionDoesNotExistException, MemberAgreementRequiredException, MissingParameterException
from accounts.mbo_client_manager import SignUpManager, ClientSetting
from slicerepublic.sendmail import send_studio_user_signup_verification_mail
from venues.exceptions import StudioDoesNotExistException

from accounts.auth_request import UserAuthRequest

from accounts.validators import UserValidator

from slicerepublic import exceptions

from django.conf import settings
from accounts.models import CustomToken, AppVersion, User, MboClient

from accounts.serializers import UserSerializer, AppVersionSerializer, MboClientSettingSerializer

import logging
from venues.models import Studio


class TokenView(APIView):
    """
    Only mbo users are allowed in this release
    """

    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):

        auth_request = UserAuthRequest(request)
        auth_request.validate()

        username, password, studio_id = auth_request.get_data()
        device_info = None
        if 'HTTP_DEVICE_INFO' in request.META:
            device_info = request.META['HTTP_DEVICE_INFO']
            self.logger.debug("HTTP_DEVICE_INFO : {}".format(device_info))

        validate = UserValidator(username, password, studio_id)
        user = validate()

        if device_info:
            validate.track_device_information(device_info)

        token = validate.get_or_create_token(user)
        return Response({'token': token[0].key}, status=status.HTTP_201_CREATED)


class Logout(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):
        data = request.DATA

        self.logger.info("Log out the user {}".format(request.user.id))
        CustomToken.objects.filter(key=request.auth.key).delete()
        clear_push_notification_instance(request, data)

        self.logger.debug("Leaving Logout view")
        return Response(status=status.HTTP_200_OK)


class GetUser(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered GetUser view (username : {})".format(request.user.email))
        serializer = UserSerializer(request.user, context={'home_studio': request.auth.studio})
        self.logger.info("Leaving GetUser view")
        return Response(serializer.data, status=status.HTTP_200_OK)


class MemberAgreementView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered get member agreement view.")
        member_agreement_status = get_member_agreement_status(request.user)

        self.logger.info("Leaving get member agreement view.")
        content = {'accepted': member_agreement_status}
        return Response(content, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        self.logger.info("Entered update member agreement view.")
        member_agreement_status = self.get_member_agreement_status()
        if not member_agreement_status:
            message = "accepted: Required parameter missing"
            self.logger.error(message)
            raise MemberAgreementRequiredException("40060", "Missing Parameter", message)
        update_member_agreement_status(request.user, member_agreement_status)
        self.logger.info("Leaving update member agreement view.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_member_agreement_status(self):
        return self.request.GET.get('accepted')


class AppVersionView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, platform):
        app_version = AppVersion.objects.get_app_version_by_platform(platform)

        if not app_version:
            self.logger.error("App version for the platform {} is not found!".format(platform))
            raise AppVersionDoesNotExistException("40040", "Not found", "App version is not found")

        serializer = AppVersionSerializer(app_version)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequiredFieldList(APIView):
    def get(self, request, pk, format=None):
        fields = get_required_fields_by_studio_id(pk)
        return Response(fields, status=status.HTTP_200_OK)


class UserSignupView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):
            try:
                data = request.DATA
            except ParseError as error:
                message = "Invalid Format - {0}".format(error.detail)
                self.logger.error(message)
                raise exceptions.ParseError(40080, "Malformed request.", message)

            if "username" not in data:
                message = "username : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            if "password" not in data:
                message = "password : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            if "studio_id" not in data:
                message = "studio_id : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            if "first_name" not in data:
                message = "first_name : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            if "last_name" not in data:
                message = "last_name : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            try:
                studio = Studio.objects.get_studio_by_studio_id(data.__getitem__('studio_id'))
            except Studio.DoesNotExist:
                    message = "Invalid studio id"
                    raise StudioDoesNotExistException("40000", "Studio does not exist", message)

            signup_manager = SignUpManager(data)
            client_info = signup_manager._populate_client_info()

            signup_user_to_studio(client_info, studio)
            return Response(status=status.HTTP_201_CREATED)


class UsersSearchView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request):
        email, studio_id = self.get_params()
        self.logger.info("Entered search view (email: {}, studio_id: {})".format(email, studio_id))

        if self.validate(email, studio_id):
            user = search_user(email, studio_id)
            studio = Studio.objects.get_studio_by_studio_id(studio_id)

            if not user:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user, context={'home_studio': studio})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_params(self):
        email = self.request.GET.get('email')
        studio_id = self.request.GET.get('studio_id')
        return email, studio_id

    def validate(self, email, studio_id):
        if email and studio_id:
            return True
        else:
            return False


class VerificationEmailView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request):
        email = self.request.GET.get('email')
        verification_hash = get_verification_hash_for_user(email)
        host_name = settings.SIGNUP_VERIFICATION_HOST_NAME
        send_studio_user_signup_verification_mail(host_name, email, verification_hash, email)

        return Response(status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):
        data = request.DATA
        if "email" not in data:
            message = "email : Required parameter missing"
            self.logger.error(message)
            raise MissingParameterException("40010", "Missing Parameter", message)

        if "studio_id" not in data:
            message = "studio_id : Required parameter missing"
            self.logger.error(message)
            raise MissingParameterException("40010", "Missing Parameter", message)

        email = data.__getitem__('email')
        studio_id = data.__getitem__('studio_id')
        send_link_to_user_to_set_new_password(email, studio_id)

        return Response(status=status.HTTP_200_OK)


class MboClientSettingView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered MboClientSetting get View for user: {}".format(request.user.email))
        client_setting = ClientSetting(request)
        setting = client_setting.get_client_setting_for_mbo_client()
        serializer = MboClientSettingSerializer(setting)
        self.logger.info("Leaving MboClientSettingView")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        self.logger.info("Entered MboClientSetting post View for user: {}".format(request.user.email))
        is_enable = self.get_params(request)

        client_setting = ClientSetting(request)
        client_setting.update(is_enable)
        self.logger.info("Leaving MboClientSettingView")
        return Response(status=status.HTTP_200_OK)

    def get_params(self,  request):
        if request.query_params and request.query_params['is_enable']:
            return request.query_params['is_enable']

        raise MissingParameterException("40010", "Missing Parameter", "Missing Parameter: is_enable")


class GetUserList(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        self.logger.info("Entering into GetUserList view.")
        page = self.get_page()
        search_filters = self.get_search_filters()
        count = MboClient.objects.count(**search_filters)
        mbo_users = MboClient.objects.search(page, **search_filters)
        results = MboClient.get_results(mbo_users)

        response = {}
        response['count'] = count
        response['users'] = results

        self.logger.info("Leaving from GetUserList view.")
        return Response(response, status=status.HTTP_200_OK)

    def get_page(self):
        page = self.request.query_params.get('page')
        if page:
            return int(page)

    def get_search_filters(self):
            query_param_keys = [
                'email',
                'first_name',
                'last_name',
                'start_date',
                'end_date',
                'studio',
            ]

            kwargs = {}
            for key in query_param_keys:
                if self.request.query_params.get(key):
                    kwargs[key] = self.request.query_params.get(key)

            return kwargs
