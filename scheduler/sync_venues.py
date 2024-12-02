from venues.models import Studio
from venues.venue_manager import handle_location_from_mbo, handle_resource_from_mbo
from mind_body_service import site_api
from django.db import transaction


@transaction.atomic
def sync_locations(mbo_site_id, force_update=False):
    studio = Studio.objects.filter(mbo_site_id=mbo_site_id).first()

    if not studio:
        print("Studio with mbo site id {} not found!".format(mbo_site_id))
        return

    print("Synchronizing locations of the studio {}".format(mbo_site_id))

    get_locations_result = site_api.get_locations(mbo_site_id)

    status = get_locations_result.Status
    if status == 'Invalid Credentials':
        raise Exception('InvalidCredentials')

    result_count = get_locations_result.ResultCount
    total_page_count = get_locations_result.TotalPageCount
    print('Resul Count : {}'.format(result_count))
    print('Total Page Count : {}'.format(total_page_count))

    if get_locations_result.Locations == 0:
        print('There is no location in Mindbody to synchronize!')
        return

    for mbo_location in get_locations_result.Locations[0]:
        if not mbo_location.Latitude or not mbo_location.Longitude:
            print('Location ({}) does not have Lat or Lng, hence not synchronizing!'.format(mbo_location.ID))
            continue
        print('Synchronizing location {} - {}'.format(mbo_location.Name, mbo_location.ID))
        handle_location_from_mbo(mbo_location, studio)


@transaction.atomic
def sync_resources(mbo_site_id, force_update=False):
    studio = Studio.objects.filter(mbo_site_id=mbo_site_id).first()

    if not studio:
        print('Studio with mbo site id {} not found!'.format(mbo_site_id))
        return

    # In future can bind a resource to a location. It is not necessary for now.
    mbo_resources = site_api.get_resources(mbo_site_id=studio.mbo_site_id)
    result_count = mbo_resources.ResultCount
    total_page_count = mbo_resources.TotalPageCount

    if result_count > 0:
        for mbo_resource in mbo_resources.Resources[0]:
            print("Handling resource {}".format(mbo_resource.Name))
            handle_resource_from_mbo(mbo_resource, studio)

    if total_page_count > 1:
        for page in range(1, total_page_count):
            sync_resources_page_by_page(studio, page)


def sync_resources_page_by_page(studio, page):
    mbo_resources = site_api.get_resources(studio.mbo_site_id, page)
    if mbo_resources.ResultCount > 0:
        for mbo_resource in mbo_resources.Resources[0]:
            print("Handling resource {}".format(mbo_resource.Name))
            handle_resource_from_mbo(mbo_resource, studio)
