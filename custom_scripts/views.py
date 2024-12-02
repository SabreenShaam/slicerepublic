from rest_framework import status
from rest_framework.views import APIView
from classes.models import SliceClass, Program
from mind_body_online.ClientService import ClientServiceCalls
from rest_framework.response import Response
from django.conf import settings
import logging
from mind_body_service.client_api import get_client_by_email
from mind_body_service.sale_api import checkout_complimentary_shopping_cart_item

logger = logging.getLogger(__name__)


class ScriptCreateUserView(APIView):
    logger = logging.getLogger(__name__)

    def post(self, request, format=None):
        emails = ["jamesarnold_281@yahoo.com", "olga1@hotyogasociety.com", "helle1@gym-class.co.uk",
                  "michele1@fiercegrace.com", "aimee1@barrecore.co.uk "]
        passwords = ['yG:S?/9D', '{j6vB\@K', 'p>(3upM9', 'yq&6}WMR', 'G6N@g`nc']
        for val in emails:
            client_info = {}
            client_info.setdefault("Username", val)
            client_info.setdefault("Email", val)
            client_info.setdefault("Password", passwords[emails.index(val)])
            client_info.setdefault("FirstName", "TestUser" + str(emails.index(val)))
            client_info.setdefault("LastName", "TestUserStudio" + str(emails.index(val)))
            client_info.setdefault("BirthDate", "1990-10-10")
            response = self.add_client(client_info, -99)
            if response.Status != "Success":
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.logger.info("Test User Created with email {} password {}".format(val, passwords[emails.index(val)]))
        return Response(status=status.HTTP_200_OK)

    def add_client(self, clients, mbo_site_id):
        client_service = ClientServiceCalls()
        response = client_service.AddOrUpdateClients(
            updateAction="AddNew",
            clients=clients,
            mbo_site_ids=[mbo_site_id],
            mbo_username=settings.MBO_STAFF_USERNAME,
            mbo_password=settings.MBO_STAFF_PASSWORD,
        )

        if response.Status != "Success":
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
        return response


class BuyPricingOptions(APIView):
    logger = logging.getLogger(__name__)

    def post(self, request, format=None):
        emails = ["jamesarnold_281@yahoo.com", "olga1@hotyogasociety.com", "helle1@gym-class.co.uk",
                  "michele1@fiercegrace.com", "aimee1@barrecore.co.uk "]
        mbo_site_id = -99
        mbo_service_id = 1419
        staff_username = settings.MBO_STAFF_USERNAME
        staff_password = settings.MBO_STAFF_PASSWORD
        for email in emails:
            client = get_client_by_email(email, staff_username, staff_password, mbo_site_id)
            if client.Clients:
                mbo_client_id = client.Clients.Client[0].ID
                checkout_complimentary_shopping_cart_item(mbo_client_id, mbo_service_id, mbo_site_id, staff_username,
                                                          staff_password)
                self.logger.info(email + " " + mbo_client_id)
            else:
                self.logger.info("Not found " + email + " ")

        return Response(status=status.HTTP_200_OK)


class PopulateProgramForClassView(APIView):
    def get(self, request, format=None):
        classes = SliceClass.objects.select_related('studio', 'session_type').all()
        for item in classes:
            program = Program.objects.get_program_by_mbo_program_id_and_studio(item.session_type.program_id,
                                                                               item.studio.id)
            item.program = program
            item.save()

        return Response(status=status.HTTP_200_OK)
