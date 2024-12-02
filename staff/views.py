from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.auth_request import UserAuthRequest
from staff.validators import StaffValidator

import logging


class StaffValidationView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        return Response({'detail': 'Method "GET" not allowed'})

    def post(self, request, format=None):
        auth_request = UserAuthRequest(request)
        auth_request.validate()

        username, password, studio_id = auth_request.get_data()

        validate = StaffValidator(username, password, studio_id)
        validate()

        self.logger.info("Entered token view (username : {}, studio id : {})".format(username, studio_id))
        return Response(status=status.HTTP_200_OK)

