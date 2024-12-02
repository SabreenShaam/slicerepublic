from accounts.exceptions import StudioAccessDoesNotExist
from .models import MBOLocation, MBOResource, Studio
from django.db.models import Count
from studios.studios_web.models import StudioAccess
from venues.exceptions import StudioDoesNotExistException
from venues.models import StudioPricing

from venues.venue_mapper import map_values_from_mbo_location_to_location, \
    update_values_from_mbo_location_to_slice_location
import logging

logger = logging.getLogger(__name__)


def get_mbo_location(mbo_location, studio):
    mbo_location = MBOLocation.objects.get_mbolocation_by_studio_id_and_mbo_location_id(studio.id, mbo_location.ID)
    return mbo_location


def handle_location_from_mbo(mbo_location, studio, force_update=False):
    mbolocation = MBOLocation.objects.get_mbolocation_by_studio_id_and_mbo_location_id(studio.id,
                                                                                       mbo_location.ID)
    if mbolocation:
        # This will update not only MBOLocation but also associated Location.
        location = mbolocation.location
        update_location(location, mbo_location)
    else:
        location = create_location(mbo_location)
        create_mbolocation(location, studio, mbo_location.ID)


def create_location(mbo_location):
    location = map_values_from_mbo_location_to_location(mbo_location)
    location.save()
    print("Created Location {}".format(location.id))
    return location


def create_mbolocation(location, studio, mbo_location_id):
    mbolocation = MBOLocation()
    mbolocation.location = location
    mbolocation.mbo_location_id = mbo_location_id
    mbolocation.studio = studio
    mbolocation.save()
    print("Created MBOLocation {}".format(mbolocation.id))


def update_location(location, mbo_location):
    if not should_update_location(location, mbo_location):
        return
    update_values_from_mbo_location_to_slice_location(location, mbo_location)
    location.save()
    print("Updated location {}".format(location.id))


def should_update_location(location, mbo_location):
    if location.name != mbo_location.Name:
        return True

    if location.address_line_1 != mbo_location.Address:
        return True

    if location.address_line_2 != mbo_location.Address2:
        return True

    if location.city != mbo_location.City:
        return True

    if location.phone != mbo_location.Phone:
        return True

    if hasattr(mbo_location, 'BusinessDescription'):
        if location.business_description != mbo_location.BusinessDescription:
            return True
    if hasattr(mbo_location, 'PostalCode'):
        if location.postcode != mbo_location.PostalCode:
            return True
    if hasattr(mbo_location, 'Latitude'):
        if float(location.latitude) != mbo_location.Latitude:
            return True
    if hasattr(mbo_location, 'Longitude'):
        if float(location.longitude) != mbo_location.Longitude:
            return True
    if hasattr(mbo_location, 'Description'):
        if location.description != mbo_location.Description:
            return True

    return False


def handle_resource_from_mbo(mbo_resource, studio):
    mboresource = MBOResource.objects.get_mboresource_by_studio_id_and_mbo_resource_id(studio.id, mbo_resource.ID)

    # No need to handle deleting a resource.
    if mboresource:
        # Update
        if mboresource.name != mbo_resource.Name:
            mboresource.name = mbo_resource.Name
            mboresource.save()
    else:
        # Create Resource
        mboresource = MBOResource()
        mboresource.name = mbo_resource.Name
        mboresource.studio = studio
        mboresource.mbo_resource_id = mbo_resource.ID
        mboresource.save()
        # print('Created resource {}'.format(mbo_resource.Name))


def get_number_of_locations_of_studios():
    # Get the number of locations each studio has. It is used to display the location name. If the studio has more
    # than one location then format the location name displayed as "StudioName - LocationName".
    mbolocation_result = MBOLocation.objects.all().values('studio_id').annotate(num_location=Count('studio_id'))

    studio_location_count = {}
    for mbolocation in mbolocation_result:
        studio_location_count[mbolocation['studio_id']] = mbolocation['num_location']

    return studio_location_count


def get_studio_info_by_id(pk):
    try:
        studio = Studio.objects.get_studio_by_studio_id(pk)
    except Studio.DoesNotExist:
        message = "Studio does not exist for given id"
        logger.info(message)
        raise StudioDoesNotExistException("40000", "Studio does not exist", message)

    return studio


class StudioAccessList(object):
    logger = logging.getLogger(__name__)

    @staticmethod
    def _populate_access_list(raw_access_list, studio_id):
        access_list = []
        for item in raw_access_list:
            access_list_item = {}
            access_list_item['id'] = item.id
            access_list_item['name'] = item.other_studio.name

            if item.is_accessible:
                access_list_item['has_access'] = True if item.is_accessible == 1 else False
            else:
                access_list_item['has_access'] = False

            access_list.append(access_list_item)

        return access_list

    @staticmethod
    def get_external_studio_access_list(studio_id):
        raw_access_list = StudioAccess.objects.get_studio_access_list_for_studio(
            studio_id)  # Studio.objects.get_external_studio_access_list(studio_id)
        access_list = StudioAccessList._populate_access_list(raw_access_list, studio_id)
        logger.debug("Studio access list : {}".format(access_list))
        return access_list

    def update_or_create_studio_access(self, studio_id, ext_studio_id, is_accessible):
        studio_access = StudioAccess.objects.get_studio_access_item_by_studios(studio_id, ext_studio_id)

        # if not studio_access:
        #     StudioAccess.objects.create_studio_access(studio_id, ext_studio_id, is_accessible)
        #     logger.error("Studio access created for studio id {} with ext_studio_id {}".format(studio_id, ext_studio_id))
        #
        # else:
        if is_accessible == 'true':
            studio_access.is_accessible = True
        elif is_accessible == 'false':
            studio_access.is_accessible = False
        studio_access.save()
        logger.error("Studio access updated for studio id {} with ext_studio_id {}".format(studio_id, ext_studio_id))


def get_allowed_studios_for_user(user, studio):
    studios = []
    from classes.class_manager import get_studio_access_list
    studio_ids = get_studio_access_list(user, studio)
    for studio_id in studio_ids:
        studio = Studio.objects.get_studio_by_studio_id(studio_id)
        studios.append(studio)
    return studios


def get_all_studio_pricing():
    studio_pricing = StudioPricing.objects.get_all_studio_pricing()
    return studio_pricing


def update_studio_pricing_by_id(studio_id, drop_in_price, ten_pack_price):
    studio_pricing = StudioPricing.objects.get_studio_pricing_by_id(studio_id)

    if drop_in_price is not None and ten_pack_price is not None:
        studio_pricing.deactivate()
        StudioPricing.objects.create(studio_id=studio_pricing.studio.id, drop_in_price=drop_in_price,
                                     ten_pack_price=ten_pack_price)
    elif drop_in_price is not None and ten_pack_price is None:
        studio_pricing.deactivate()
        StudioPricing.objects.create(studio_id=studio_pricing.studio.id, drop_in_price=drop_in_price,
                                     ten_pack_price=studio_pricing.ten_pack_price)

    elif drop_in_price is None and ten_pack_price is not None:
        studio_pricing.deactivate()
        StudioPricing.objects.create(studio_id=studio_pricing.studio.id, drop_in_price=studio_pricing.drop_in_price,
                                     ten_pack_price=ten_pack_price)

    logger.debug("Updated studio pricing for studio_id {}".format(studio_id))


def get_studio_pricing_by_studio(id):
    studio_pricing = StudioPricing.objects.get_studio_pricing_by_studio_id(id)
    return studio_pricing
