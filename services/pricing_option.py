from datetime import timedelta
from classes.models import Program
from services.exceptions import ForbiddenException
from services.models import StudioService, MboClientService
from services.service_manager import get_client_credit_card, checked_cart_item_for_stored_credit_card, \
    get_client_services_program_by_program, sync_studio_services
import logging
from slicerepublic import dateutil
from django.conf import settings
from slicerepublic.sendmail import send_auto_pay_update_notify_email


class PricingOption(object):
    logger = logging.getLogger(__name__)

    def __init__(self, mbo_client):
        self.mbo_client = mbo_client
        self.current_client_service = None

    def get_current_service(self):
        self.current_client_service = self.get_active_client_service()
        if not self.current_client_service:
            return
        return self.current_client_service

    def handle_auto_pay(self):
        self.logger.info("Entered to handle_auto_pay")
        if not self.current_client_service:
            return

        local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")

        mbo_client_services = MboClientService.objects.get_active_services_by_names(self.mbo_client, local_dt,
                                                                                    [self.current_client_service.Name])
        if len(mbo_client_services) > 1:
            return

        mbo_client_service = mbo_client_services.first()

        if mbo_client_service:
            if mbo_client_service.auto_pay:
                if self.current_client_service.Remaining == 1:
                    credit_card = get_client_credit_card(self.mbo_client.user, self.mbo_client.studio)
                    if not credit_card:
                        self.logger.error('Stored card not found for {} user'.format(self.mbo_client.user.email))
                        return

                    sync_studio_services(self.mbo_client.studio)
                    studio_service = StudioService.objects.get_mbo_service_by_name_and_studio(self.current_client_service.Name,
                                                                                              self.mbo_client.studio)
                    if studio_service:
                        checked_cart_item_for_stored_credit_card(self.mbo_client.user, self.mbo_client.studio,
                                                                 studio_service.id)
                    else:
                        self.logger.error('Studio service not found for name   {}'.format(self.current_client_service.Name))
        self.logger.info("Leaving handle_auto_pay")

    def get_active_client_service(self):
        mbo_program_ids_result = Program.objects.get_integrated_program_id_list_by_studio(self.mbo_client.studio)
        mbo_program_ids = [entry for entry in mbo_program_ids_result]
        start_date = dateutil.utcnow_plus(timedelta(days=-settings.CLIENT_SERVICES_TIMEDELTA_INTERVAL))
        end_date = dateutil.utcnow_plus(timedelta(days=settings.CLIENT_SERVICES_TIMEDELTA_INTERVAL))
        mbo_services = get_client_services_program_by_program(self.mbo_client.mbo_client_id,
                                                              self.mbo_client.studio.mbo_site_id, mbo_program_ids,
                                                              start_date, end_date, True)
        if mbo_services:
            return mbo_services[0]
        return

    @staticmethod
    def update_auto_pay_status(id, status):
        logger = logging.getLogger(__name__)

        mbo_client_service = MboClientService.objects.get(id=id)
        if not mbo_client_service:
            logger.error('MboClientService not found for id {}'.format(id))

        if status == 'on':
            auto_pay = True
        else:
            auto_pay = False

        mbo_client_service.update_auto_pay(auto_pay)
        logger.info('MboClientService Updated')
        return mbo_client_service

    def __raise_exception(self):
        message = "No Stored Credit Card found"
        self.logger.error(message)
        raise ForbiddenException("50300", "Stored Credit Card Not found", message)

    @staticmethod
    def send_email(name, email):
        send_auto_pay_update_notify_email(name, email)
