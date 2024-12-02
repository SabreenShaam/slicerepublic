import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.authentication import CustomTokenAuthentication
from accounts.models import MboClient
from ratings.ClassRating import ClassRating
from ratings.serializers import RateSerializer


class RatingsView(APIView):
    logger = logging.getLogger(__name__)

    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        self.logger.info("Entered GET RatingsView (class_id : {}".format(pk))

        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(request.user, request.auth.studio)

        rating = ClassRating(pk, mbo_client).get_rating()

        #serializer = RateSerializer(rating)
        self.logger.info("Leaving GET RatingsView")
        return Response(rating, status=status.HTTP_200_OK)

    def post(self, request, pk, format=None):
        self.logger.info("Entered POST RatingsView")

        value = self.get_rate()
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(request.user, request.auth.studio)
        rating = ClassRating(pk, mbo_client)
        rating.rate(value)

        self.logger.info("Leaving POST RatingsView")
        return Response(status=status.HTTP_200_OK)

    def get_rate(self):
        rate = self.request.query_params.get('rate')
        return rate
