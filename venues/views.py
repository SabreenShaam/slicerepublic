from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.authentication import CustomTokenAuthentication
from accounts.exceptions import MissingParameterException
from venues.models import Studio
from venues.serializers import StudioSerializer, StudioPricingSerializer
from venues.venue_manager import get_studio_info_by_id, StudioAccessList, get_allowed_studios_for_user, \
    get_all_studio_pricing, \
    update_studio_pricing_by_id, get_studio_pricing_by_studio
import logging


class StudioList(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)

    def get(self, request, format=None):
        user = request.user
        if user.is_anonymous():
            studios = Studio.objects.get_all_active_mbo_studios()
        else:
            # TODO : can use request.query_params.get('allowed')
            if self.request.QUERY_PARAMS and 'allowed' in self.request.QUERY_PARAMS:
                allowed = self.request.QUERY_PARAMS['allowed']
                if allowed == 'True':
                    studios = get_allowed_studios_for_user(request.user, request.auth.studio)
            else:
                message = "allowed : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

        if len(studios) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = StudioSerializer(studios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudioInfoView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk):
        self.logger.info("Entered StudioInfo View (studio id : {})".format(pk))
        studio = get_studio_info_by_id(pk)

        serializer = StudioSerializer([studio], many=True)
        self.logger.info("Leaving StudioInfo View (studio id : {})".format(pk))
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetStudioAccessListView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk):
        self.logger.info("Entered GetStudioAccessList View")
        studio_access_list = StudioAccessList()
        list_items = studio_access_list.get_external_studio_access_list(pk)

        self.logger.info("Leaving StudioAccessList View")
        return Response(list_items, status=status.HTTP_200_OK)


class UpdateStudioAccessListView(APIView):
    logger = logging.getLogger(__name__)

    def post(self, request, studio_id, ext_studio_id):
        self.logger.info("Entered UpdateStudioAccessList View")
        if request.QUERY_PARAMS:
            is_accessible = request.QUERY_PARAMS['is_accessible']
            studio_access_list = StudioAccessList()
            studio_access_list.update_or_create_studio_access(studio_id, ext_studio_id, is_accessible)
            return Response(status=status.HTTP_200_OK)
        self.logger.info("Leaving UpdateStudioAccessList View")


class StudioPricingView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, Format=None):
        self.logger.debug("Entered StudioPricingView GET")

        all_studio_pricing = get_all_studio_pricing()
        serializer = StudioPricingSerializer(all_studio_pricing, many=True)

        self.logger.debug("Leaving StudioPricingView GET")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, Format=None):
        self.logger.debug("Entered StudioPricingView POST")

        studio_id = self.get_studio_id()
        drop_in_price = self.get_drop_in_price()
        ten_pack_price = self.get_ten_pack_price()

        update_studio_pricing_by_id(studio_id, drop_in_price, ten_pack_price)
        self.logger.debug("Leaving StudioPricingView POST")

        return Response(status=status.HTTP_200_OK)

    def get_drop_in_price(self):
        if "one_pack_drop_in" in self.request.DATA:
            return self.request.DATA.__getitem__('one_pack_drop_in')

        return None

    def get_ten_pack_price(self):
        if "ten_pack_drop_in" in self.request.DATA:
            return self.request.DATA.__getitem__('ten_pack_drop_in')

        return None

    def get_studio_id(self):
        if "studio_id" not in self.request.DATA:
            message = "id : Required parameter missing"
            self.logger.error(message)
            raise MissingParameterException("40010", "Missing Parameter", message)
        return self.request.DATA.__getitem__('studio_id')


class StudioPricingInfoView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk, Format=None):
        self.logger.debug("Entered StudioPricingInfoView GET")

        pricing = get_studio_pricing_by_studio(pk)
        serializer = StudioPricingSerializer(pricing)

        self.logger.debug("Leaving StudioPricingInfoView GET")
        return Response(serializer.data, status=status.HTTP_200_OK)
