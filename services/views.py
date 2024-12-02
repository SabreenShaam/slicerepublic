from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.authentication import CustomTokenAuthentication
from accounts.exceptions import MissingParameterException

from accounts.models import MboClient
from services.models import StudioService

from venues.models import Studio

from services.service_manager import get_all_client_services, checkout_shopping_cart, \
    get_checkout_summary, get_studio_service_list, get_client_credit_card, checked_cart_item_for_stored_credit_card, \
    client_services_sync, create_or_update_mbo_service, get_mbo_services, activate_auto_pay, update_mbo_service_state, \
    get_mbo_client_service_info, update_passport_access, get_studio_access_by_mbo_service, populate_studio_access_list

from services.serializer import MboClientServiceSerializer, StudioServiceSerializer, ClientCreditCardSerializer, \
    PassportStudioAccessSerializer

import logging


class ClientServiceView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)

    def get(self, request, format=None):
        self.logger.info("Entered ClientServiceView [user : {}]".format(request.user.email))

        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=request.user, studio=request.auth.studio)

        client_services_sync(mbo_client)
        services = get_all_client_services(mbo_client)

        serializer = MboClientServiceSerializer(services, many=True)
        self.logger.info("Leaving ClientServiceView [user : {}]".format(request.user.email))
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckoutServiceView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        self.logger.debug("Entered CheckoutServiceView [user_id {}, service_id {}]".format(request.user.id, pk))
        studio_service = StudioService.objects.get_studio_service_by_id(pk)

        if not studio_service:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.DATA
        card_number = data.__getitem__('card_number')
        name = data.__getitem__('username')
        expiration_year = data.__getitem__('expire_year')
        expiration_month = data.__getitem__('expire_month')

        response = checkout_shopping_cart(request.user, request.auth.studio, studio_service, name, card_number,
                                          expiration_year, expiration_month)

        if self.get_auto_pay_param():
            activate_auto_pay(request.user, request.auth.studio, response)

        self.logger.debug("Leaving CheckoutService View")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_auto_pay_param(self):
        if self.request.query_params and self.request.query_params['autopay'] == 'True':
            return self.request.query_params['autopay']
        return None


class StudioServiceListView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=request.user, studio=request.auth.studio)

        studio_services = get_studio_service_list(mbo_client.studio)
        serializer = StudioServiceSerializer(studio_services, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceSummaryView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        self.logger.debug("Entered service summary view [user_id : {}, service_id : {}]".format(request.user.id, pk))
        studio_service = StudioService.objects.get_studio_service_by_id(pk)

        if not studio_service:
            return Response(status.HTTP_404_NOT_FOUND)

        checkout_summary = get_checkout_summary(request.user, request.auth.studio, studio_service)
        self.logger.debug("Leaving service summary view [user_id : {}, service_id : {}]".format(request.user.id, pk))
        return Response(checkout_summary, status=status.HTTP_200_OK)


class ClientCreditCardInfoView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.debug("Entered ClientCreditCardInfoView [user : {}]".format(request.user.email))
        credit_card = get_client_credit_card(request.user, request.auth.studio)

        if not credit_card:
            self.logger.debug("Leaving ClientCreditCardInfoView, No Credit Card found!")
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ClientCreditCardSerializer(credit_card)
        self.logger.debug("Leaving ClientCreditCardInfoView")
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoredCardCheckoutView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, pk, format=None):
        self.logger.debug(
            "Entered StoredCardCheckoutView [user : {}, credit_card_id : {}]".format(request.user.email, pk))
        response = checked_cart_item_for_stored_credit_card(request.user, request.auth.studio, pk)

        if self.get_auto_pay_param():
            activate_auto_pay(request.user, request.auth.studio, response)

        self.logger.debug("Leaving StoredCardCheckoutView")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_auto_pay_param(self):
        if self.request.query_params and self.request.query_params['autopay'] == 'True':
            return self.request.query_params['autopay']
        return None


class MboServiceUpdateView(APIView):
    logger = logging.getLogger(__name__)

    def post(self, request, format=None):
        self.logger.info("Entered into MboServiceUpdate View")
        if request.DATA and 'state' not in request.DATA:
            service_id = request.DATA['service_id']
            studio_id = request.DATA['studio_id']
            count = request.DATA['count']

            max_per_studio_count = request.DATA['max_per_studio_count']
            create_or_update_mbo_service(service_id, studio_id, count, max_per_studio_count)
            self.logger.info("Leaving MboServiceUpdate View")
            return Response(status=status.HTTP_200_OK)
        else:
            studio_id = request.DATA['studio_id']
            service_id = request.DATA['service_id']
            state = request.DATA['state']
            update_mbo_service_state(service_id, studio_id, state)

            return Response(status=status.HTTP_200_OK)


class MboServiceSummaryView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        self.logger.info("Entered into MboServiceSummary View")
        if request.DATA:
            studio_id = request.DATA['studio_id']
            mbo_services = get_mbo_services(studio_id)
            if not mbo_services:
                return Response(status=status.HTTP_404_NOT_FOUND)

            self.logger.info("Leaving MboServiceSummary View")
            return Response(mbo_services, status=status.HTTP_200_OK)


class StudioPortalServicesView(APIView):
    logger = logging.getLogger(__name__)

    def post(self, request, format=None):
        self.logger.info("Entered into StudioPortalServices View")
        if request.DATA:
            if 'studio_id' in request.DATA:
                studio_id = request.DATA['studio_id']
                studio = Studio.objects.get_studio_by_studio_id(studio_id)
                studio_services = get_studio_service_list(studio)

        serializer = StudioServiceSerializer(studio_services, many=True)
        self.logger.info("Leaving StudioPortalServices View")
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateAutoPayOption(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, state, format=None):
        self.logger.debug("Entered UpdateAutoPayOption view [user_id {}, service_id {}]".format(request.user.id, pk))
        from services.pricing_option import PricingOption
        mbo_client_service = PricingOption.update_auto_pay_status(pk, state)
        if mbo_client_service:
            PricingOption.send_email(mbo_client_service.name, request.user.email)
            PricingOption.send_email(mbo_client_service.name, request.auth.studio.contact_email)

        self.logger.debug(
            "Leaving service UpdateAutoPayOption view [user_id : {}, service_id : {}]".format(request.user.id, pk))
        return Response(status=status.HTTP_200_OK)


class ClientServiceInfoView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        self.logger.info("Entered into ClientServiceInfoView")
        mbo_client_service = get_mbo_client_service_info(pk)
        if mbo_client_service:
            self.logger.debug("Leaving ClientServiceInfoView")
            return Response(mbo_client_service, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class PassportStudioAccessView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk, format=None):
        result = populate_studio_access_list(pk)
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request, pk, format=None):
        self.logger.info("Entered into PassportAccessView(post)")
        is_accessible = self.get_is_accessible()
        update_passport_access(pk, is_accessible)
        self.logger.info("Leaving PassportAccessView(post)")
        return Response(status=status.HTTP_200_OK)

    def get_is_accessible(self):
        is_accessible = self.request.query_params.get('is_accessible')
        if not is_accessible:
            raise MissingParameterException("40010", "Missing Parameter", "Missing Parameter: is_accessible")
        return is_accessible
