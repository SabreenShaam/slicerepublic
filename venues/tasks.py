import logging
from mind_body_service.site_api import get_site
from slicerepublic.sendmail import send_api_integration_removal_notification
from slicerepublic.settings import FITOPIA_ADMIN_EMAIL_ADDRESSES
from venues.models import Studio
from celery.task import task
import logging

logger = logging.getLogger(__name__)


@task
def check_studio_integration():
    print('Handling when studios remove API integration')
    studios = Studio.objects.filter(is_active=True)
    for studio in studios:
        site_id = studio.mbo_site_id
        response = get_site(site_id)
        if response.Status == 'InvalidCredentials' and response.Message == 'Permission denied.':
            logger.error("{} has removed the API access".format(studio.name))
            studio.deactivate()
            send_api_integration_removal_notification(studio.name, FITOPIA_ADMIN_EMAIL_ADDRESSES)

    print('Finished Handling when studios remove API integration')
