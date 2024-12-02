from slicerepublic import dateutil
from services.models import MboService, MboClientService, PassportStudioAccess
import logging


class PassportService(object):

    @staticmethod
    def fetch_all_active_passport_services(mbo_client, class_studio):
        passport_access_items = PassportStudioAccess.objects.get_passport_services_by_studio(mbo_client.studio, class_studio)
        passport_service_names = []
        for passport_access in passport_access_items:
            passport_service_names.append(passport_access.mbo_service.name)
        mbo_client_services = MboClientService.objects.get_active_services_in_names(mbo_client, passport_service_names)
        return mbo_client_services

    @staticmethod
    def get_maximum_booking_per_studio_by_passport(service_name, studio):
        mbo_service = MboService.objects.get_mbo_service_by_name_and_studio(service_name, studio)
        return mbo_service.max_per_studio
