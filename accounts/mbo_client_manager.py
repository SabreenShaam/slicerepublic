from accounts.models import MboClientSettings, MboClient
from accounts.wrappers import ClientWrapper
from mind_body_service.client_api import add_client
import logging


class MboClientManager(object):
    def __int__(self):
        emerg_contact = {
            "EmergencyContactInfoName": "Fitopia",
            "EmergencyContactInfoRelationship": "Member",
            "EmergencyContactInfoPhone": "020 7186 6007",
            "EmergencyContactInfoEmail": "hello@fitopia.co.uk"
        }

        self.default_client_info = {"Gender": "Female",
                                    "BirthDate": "2015-10-19",
                                    "AddressLine1": "11 Heathmans Road",
                                    "City": "London",
                                    "State": "LND",
                                    "PostalCode": "SW6 4TJ",
                                    "MobilePhone": "020 7186 6007",
                                    "WorkPhone": "020 7186 6007",
                                    "HomePhone": "020 7186 6007",
                                    "ReferredBy": "Fitopia",
                                    "MiddleName": "Fitopia",
                                    "EmergContact": emerg_contact
                                    }

    def create_external_client(self, mbo_site_id, user):
        required_fields = ClientWrapper.get_required_client_fields(mbo_site_id)
        client = self.__populate_external_client(user, required_fields)
        response = add_client(client, mbo_site_id)
        return response

    @staticmethod
    def generate_client_id(number):
        client_id = "Fit{0:010d}".format(number)
        return client_id

    @staticmethod
    def generate_email(client_id):
        email = "{}@fitopia.co.uk".format(client_id)
        return email

    def __populate_external_client(self, user, required_fields):
        client_id = MboClientManager.generate_client_id(user.id)

        client = {}
        client['ID'] = client_id
        client['FirstName'] = user.first_name
        client['LastName'] = user.last_name
        client['Email'] = MboClientManager.generate_email(client_id)

        for field in required_fields:
            if field == 'IsMale':
                field = 'Gender'
            if field in self.default_client_info:
                default_value = self.default_client_info[field]
                if not isinstance(default_value, dict):
                    client[field] = default_value
                else:  # added to support EmergContact which has 4 values
                    for field_name, value in default_value.items():
                        client[field_name] = value

        return client

    @staticmethod
    def update_client_info(client, mbo_client):
        if mbo_client.mbo_client_id != client.ID:
            mbo_client.update(client.ID)


class SignUpManager(object):
    logger = logging.getLogger(__name__)

    def __init__(self, data):
        self.data = data
        emerg_contact = {
                "EmergencyContactInfoName": "emerg_name",
                "EmergencyContactInfoRelationship": "emerg_relationship",
                "EmergencyContactInfoPhone": "emerg_phone",
                "EmergencyContactInfoEmail": "emerg_email"
            }

        self.mandatory_client_key_info = {"Username": "username",
                                          "Email": "username",
                                          "Password": "password",
                                          "FirstName": "first_name",
                                          "LastName": "last_name"}

        self.optional_client_key_info = {"IsMale": "gender",
                                        "BirthDate": "birth_date",
                                        "AddressLine1": "address_line1",
                                        "City": "city",
                                        "State": "state",
                                        "PostalCode": "postal_code",
                                        "MobilePhone": "mobile_phone",
                                        "WorkPhone": "work_phone",
                                        "HomePhone": "home_phone",
                                        "ReferredBy": "referred_by",
                                        "MiddleName": "middle_name",
                                        "EmergContact": emerg_contact
                                        }

    def _populate_required_fields(self, required_fields):
        required_keys = []
        for key, value in self.mandatory_client_key_info.items():
            required_keys.append(value)

        for field in required_fields:
            if field in self.optional_client_key_info.keys():
                key = self.optional_client_key_info[field]

                if field == "EmergContact":
                    for emg_key, emg_value in key.items():
                        required_keys.append(emg_value)
                else:
                    required_keys.append(key)
            else:
                self.logger.error("Key for {} field does not exist!".format(field))

        return required_keys

    def _populate_client_info(self):
        client_info = {}
        for key, value in self.mandatory_client_key_info.items():  # populate mandatory fields
            if value in self.data:
                    client_info.setdefault(key, self.data.__getitem__(value))

        for key, value in self.optional_client_key_info.items():  # populate optional fields
            if key is not "EmergContact" and key is not "IsMale":
                if value in self.data:
                    client_info.setdefault(key, self.data.__getitem__(value))
                    continue
            if key is "IsMale":
                if value in self.data:
                    client_info.setdefault("Gender", self.data.__getitem__(value))
                    continue
            elif key is "EmergContact":  # populate emergency info
                for emg_key, emg_value in value.items():
                    if emg_value in self.data:
                        client_info.setdefault(emg_key, self.data.__getitem__(emg_value))

        return client_info

    def populate_mandatory_required_fields(self):
        required_keys = []
        for key, value in self.mandatory_client_key_info.items():
            required_keys.append(value)
        return required_keys


class ClientSetting(object):
    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request
        self.mbo_client = self._fetch()

    def _fetch(self):
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=self.request.user, studio=self.request.auth.studio)
        return mbo_client

    def get_client_setting_for_mbo_client(self):
        client_setting = MboClientSettings.objects.get_or_create(mbo_client=self.mbo_client)

        return client_setting[0]

    def update(self, is_enable):
        client_setting = MboClientSettings.objects.get_mbo_client_settings(mbo_client_id=self.mbo_client.id)

        if is_enable == 'True':
            is_enable = True
        elif is_enable == 'False':
            is_enable = False

        client_setting.update(is_enable)
        self.logger.info("mbo client setting updated for id {}".format(client_setting.id))
