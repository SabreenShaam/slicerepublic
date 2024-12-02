from mind_body_service.client_api import get_required_client_fields


class ClientWrapper(object):

    @staticmethod
    def get_required_client_fields(site_id):
        response = get_required_client_fields(site_id)
        required_fields = response.RequiredClientFields.string
        return required_fields
