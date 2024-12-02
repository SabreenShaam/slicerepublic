from accounts.exceptions import InvalidLoginException
from mind_body_service.staff_api import validate_staff
from .models import Staff

import logging
from venues.models import Studio


class StaffManager(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_or_create_staff(self, mbo_staff, mbo_site_id):
        staff = Staff.objects.filter(mbo_site_id=mbo_site_id, mbo_staff_id=mbo_staff.ID).first()
        if not staff:
            staff = Staff()
            staff.mbo_site_id = mbo_site_id
            staff.mbo_staff_id = mbo_staff.ID
            staff.first_name = mbo_staff.FirstName
            staff.last_name = mbo_staff.LastName
            staff.name = mbo_staff.Name
            staff.is_male = mbo_staff.isMale

            if hasattr(mbo_staff, 'ImageURL'):
                staff.image_url = mbo_staff.ImageURL

            if hasattr(mbo_staff, 'Email'):
                staff.email = mbo_staff.Email

            if hasattr(mbo_staff, 'MobilePhone'):
                staff.mobile_phone = mbo_staff.MobilePhone.replace(" ", "")

            staff.update()
            print("Created staff {}".format(mbo_staff.ID))

        return staff

    def handle_staff_update(self, staff, mbo_staff):
        self.logger.debug("Entered handle_staff_update (slice_staff_id : {}, mbo_staff_id : {})".format(staff.id, mbo_staff.ID))
        update_required = False
        if staff.first_name != mbo_staff.FirstName:
            staff.first_name = mbo_staff.FirstName
            update_required = True

        if staff.last_name != mbo_staff.LastName:
            staff.last_name = mbo_staff.LastName
            update_required = True

        if staff.name != mbo_staff.Name:
            staff.name = mbo_staff.Name
            update_required = True

        if staff.is_male != mbo_staff.isMale:
            staff.is_male = mbo_staff.isMale
            update_required = True

        if hasattr(mbo_staff, 'ImageURL') and (staff.image_url != mbo_staff.ImageURL):
            staff.image_url = mbo_staff.ImageURL
            update_required = True

        if hasattr(mbo_staff, 'Email') and (staff.email != mbo_staff.Email):
            staff.email = mbo_staff.Email
            update_required = True

        if hasattr(mbo_staff, 'MobilePhone') and (staff.mobile_phone != mbo_staff.MobilePhone):
            staff.mobile_phone = mbo_staff.MobilePhone.replace(" ", "")
            update_required = True

        if update_required:
            staff.update()
            self.logger.info("Staff details updated (slice_staff_id : {}, mbo_staff_id : {})".format(staff.id, mbo_staff.ID))
        self.logger.debug("Leaving handle_staff_update.")
