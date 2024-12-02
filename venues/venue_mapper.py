from .models import Location


def map_values_from_mbo_location_to_location(mbo_location):
    location = Location()
    location.name = mbo_location.Name

    location.address_line_1 = mbo_location.Address
    location.address_line_2 = mbo_location.Address2
    location.city = mbo_location.City
    location.phone = mbo_location.Phone

    if hasattr(mbo_location, 'BusinessDescription'):
        location.business_description = mbo_location.BusinessDescription
    if hasattr(mbo_location, 'PostalCode'):
        location.postcode = mbo_location.PostalCode
    if hasattr(mbo_location, 'Latitude'):
        location.latitude = mbo_location.Latitude
    if hasattr(mbo_location, 'Longitude'):
        location.longitude = mbo_location.Longitude
    if hasattr(mbo_location, 'Description'):
        location.description = mbo_location.Description

    return location


# todo : there are many common code in this method and above method. Extract common code
def update_values_from_mbo_location_to_slice_location(location, mbo_location):
    location.name = mbo_location.Name

    location.address_line_1 = mbo_location.Address
    location.address_line_2 = mbo_location.Address2
    location.city = mbo_location.City
    location.phone = mbo_location.Phone

    if hasattr(mbo_location, 'BusinessDescription'):
        location.business_description = mbo_location.BusinessDescription
    if hasattr(mbo_location, 'PostalCode'):
        location.postcode = mbo_location.PostalCode
    if hasattr(mbo_location, 'Latitude'):
        location.latitude = mbo_location.Latitude
    if hasattr(mbo_location, 'Longitude'):
        location.longitude = mbo_location.Longitude
    if hasattr(mbo_location, 'Description'):
        location.description = mbo_location.Description
