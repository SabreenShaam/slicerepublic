from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from accounts.authentication import CustomTokenAuthentication
from accounts.exceptions import MissingParameterException
from fcm.FCMClient import FCMClient


class FCMInstanceView(APIView):
    logger = logging.getLogger(__name__)

    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):
        self.logger.info("Entered FCMInstanceView")
        data = request.DATA

        if "instance_id" not in data:
            message = "instance_id : Required parameter missing"
            self.logger.error(message)
            raise MissingParameterException("40010", "Missing Parameter", message)

        fcm_client = FCMClient(request, data)
        fcm_client.save()

        self.logger.info("Leave FCMInstanceView")
        return Response(status=status.HTTP_200_OK)
