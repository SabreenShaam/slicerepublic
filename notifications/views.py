from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from accounts.authentication import CustomTokenAuthentication
from accounts.exceptions import MissingParameterException
from notifications.notification_manager import NotifyManager

from rest_framework.response import Response
from rest_framework import status
from accounts.models import MboClient
import logging


class NotificationView(APIView):
    logger = logging.getLogger(__name__)

    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered into NotificationView(get)")
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=self.request.user, studio=self.request.auth.studio)
        is_handled = self.get_handled_param()

        result = NotifyManager.get_notifications(mbo_client.id, is_handled)

        self.logger.info("Leaving from NotificationView(get)")
        return Response(result, status=status.HTTP_200_OK)

    def get_handled_param(self):
        is_handled = self.request.query_params.get('handled')
        if is_handled == "True":
            return True
        else:
            return False

    def post(self, request, format=None):
            self.logger.info("Entered into NotificationView(post)")
            data = request.DATA
            if "id" not in data:
                message = "id : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            if "handled" not in data:
                message = "handled : Required parameter missing"
                self.logger.error(message)
                raise MissingParameterException("40010", "Missing Parameter", message)

            id = request.DATA.__getitem__('id')
            handled = request.DATA.__getitem__('handled')

            NotifyManager().update(id, handled)

            self.logger.info("Leaving from NotificationView(post)")
            return Response(status=status.HTTP_200_OK)
