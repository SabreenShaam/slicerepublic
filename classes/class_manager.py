from datetime import timedelta
import logging
from django.db.models import Count
from classes.mbo_class_service import MboGetClass
from .models import SliceClass, SessionType, Schedule
from accounts.models import MboClient
from services.models import MboService, PassportStudioAccess
from slicerepublic.sendmail import send_class_cancellation_emails
from venues.models import MBOResource, MBOLocation, StudioSettings, RoomLocation, Studio
from bookings.bookings_core.models import Booking
from staff.staff_manager import StaffManager
from venues.venue_manager import get_mbo_location
from services.service_manager import get_required_services_for_external_bookings
from .class_mapper import map_values_from_mbo_session_type_to_slice_session_type, \
    map_values_from_mbo_class_to_slice_class
from slicerepublic import dateutil
from slicerepublic.dateutil import make_utc
from slicerepublic.distance_util import is_inside_radius
from slicerepublic.html_stripper import strip_tags
from venues import venues_dao

logger = logging.getLogger(__name__)


def handle_class_from_mbo(mbo_class, slice_classes, studio, synced_class_ids, force_update=False):
    slice_class = next((slice_class for slice_class in slice_classes if slice_class.mbo_class_id == mbo_class.ID), None)
    if slice_class:
        synced_class_ids.append(slice_class.id)
        update_class(mbo_class, slice_class, studio, force_update)
    else:
        create_new_class(mbo_class, studio)


# Todo : Improve this method
def update_class(mbo_class, slice_class, studio, force_update=False):
    # todo: handle force update

    update_required = False
    if slice_class.is_cancelled != mbo_class.IsCanceled:
        slice_class.is_cancelled = mbo_class.IsCanceled
        update_required = True

    if slice_class.is_active != mbo_class.Active:
        slice_class.is_active = mbo_class.Active
        update_required = True

    if slice_class.mbo_last_updated != make_utc(mbo_class.ClassDescription.LastUpdated):
        slice_class.name = mbo_class.ClassDescription.Name

        if mbo_class.ClassDescription.Description:
            slice_class.description = strip_tags(mbo_class.ClassDescription.Description)
        slice_class.mbo_last_updated = make_utc(mbo_class.ClassDescription.LastUpdated)
        update_required = True

    if slice_class.staff.mbo_staff_id != mbo_class.Staff.ID:
        staff_manager = StaffManager()
        staff = staff_manager.get_or_create_staff(mbo_class.Staff, slice_class.studio.mbo_site_id)
        slice_class.staff = staff
        update_required = True
    elif slice_class.staff.mbo_staff_id == mbo_class.Staff.ID:
        staff_manager = StaffManager()
        staff_manager.handle_staff_update(slice_class.staff, mbo_class.Staff)

    if slice_class.session_type.mbo_session_type_id != mbo_class.ClassDescription.SessionType.ID:
        session_type = get_or_create_session_type(slice_class.studio.mbo_site_id, mbo_class.ClassDescription.SessionType)
        slice_class.session_type = session_type
        update_required = True
    elif slice_class.session_type.mbo_session_type_id == mbo_class.ClassDescription.SessionType.ID:
        handle_session_type_update(slice_class.session_type, mbo_class.ClassDescription.SessionType)

    if slice_class.start_date != mbo_class.StartDateTime.date():
        slice_class.start_date = mbo_class.StartDateTime.date()
        update_required = True

    if slice_class.end_date != mbo_class.EndDateTime.date():
        slice_class.end_date = mbo_class.EndDateTime.date()
        update_required = True

    if slice_class.start_time != mbo_class.StartDateTime.time():
        slice_class.start_time = mbo_class.StartDateTime.time()
        update_required = True

    if slice_class.end_time != mbo_class.EndDateTime.time():
        slice_class.end_time = mbo_class.EndDateTime.time()
        update_required = True

    if hasattr(mbo_class.ClassDescription, 'Level'):
        if slice_class.level != mbo_class.ClassDescription.Level.Name:
            slice_class.level = mbo_class.ClassDescription.Level.Name
            update_required = True

    if hasattr(mbo_class, 'Resource'):
        if slice_class.mbo_resource:
            if slice_class.mbo_resource.mbo_resource_id != mbo_class.Resource.ID:
                mbo_resource = MBOResource.objects.get_mboresource_by_studio_id_and_mbo_resource_id(studio.id, mbo_class.Resource.ID)

                if mbo_resource:
                    slice_class.mbo_resource = mbo_resource
                    update_required = True
                else:
                    logger.error("Couldn't update room ({}) for studio ({}).".format(mbo_class.Resource.Name, studio.name))
        else:
            mbo_resource = MBOResource.objects.get_mboresource_by_studio_id_and_mbo_resource_id(studio.id, mbo_class.Resource.ID)

            if mbo_resource:
                slice_class.mbo_resource = mbo_resource
                update_required = True
            else:
                logger.error("Couldn't update room ({}) for studio ({}).".format(mbo_class.Resource.Name, studio.name))

    else:
        if slice_class.mbo_resource:
            slice_class.mbo_resource = None
            update_required = True
    #TODO : need to sync session type
    if update_required:
        slice_class.save()
        #print("Updated class {}".format(mbo_class.ID))

    logger.debug("Leaving update_class.")


def create_new_class(mbo_class, studio):
    # if the class is cancelled and not in the system, don't create the class
    if mbo_class.IsCanceled:
        return

    mbolocation = get_mbo_location(mbo_class.Location, studio)

    if mbolocation is None:
        print("MBOLocation is not available for this class, hence stopping synchronization.")
        return

    # TODO : Sync staff, don't create staff when synchronizing classes
    staff_manager = StaffManager()
    staff = staff_manager.get_or_create_staff(mbo_class.Staff, mbo_class.Location.SiteID)
    # TODO : Sync session types, don't create session type when synchronizing classes
    session_type = get_or_create_session_type(mbo_class.Location.SiteID, mbo_class.ClassDescription.SessionType)

    slice_class = SliceClass()

    if hasattr(mbo_class, 'Resource'):
        mbo_resource = MBOResource.objects.get_mboresource_by_studio_id_and_mbo_resource_id(studio.id, mbo_class.Resource.ID)

        if mbo_resource:
            slice_class.mbo_resource = mbo_resource

    map_values_from_mbo_class_to_slice_class(mbo_class, slice_class, staff, mbolocation, session_type, studio)
    slice_class.save()

    #print("Created class {}".format(mbo_class.ID))


def get_or_create_session_type(mbo_site_id, mbo_session_type):
    session_type = SessionType.objects.get_sessiontype_by_mbo_sessiontype_and_site_ids(mbo_session_type.ID, mbo_site_id)
    if not session_type:
        session_type = map_values_from_mbo_session_type_to_slice_session_type(mbo_session_type, mbo_site_id)
        session_type.save()
    return session_type


def is_within_sign_in_period(start_date, start_time):
    local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    current_date = local_dt.date()
    current_time = local_dt.time()
    #print(current_date)
    #print(current_time)

    if start_date == current_date:
        sign_in_upper_dt = local_dt + timedelta(minutes=30)
        sign_in_lower_dt = local_dt + timedelta(minutes=-10)

        if sign_in_lower_dt.time() < start_time < sign_in_upper_dt.time():
            return True

    return False


def get_studio_access_list(user, studio):

    if user.is_anonymous():
        logger.debug('No studio access list found for anonymous user!')
        return None

    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user=user, studio=studio)

    studio_access_list = set()
    required_services = get_required_services_for_external_bookings(mbo_client)
    if required_services:
        logger.debug("This user has access to other studios' classes.")
        required_services_names = [service['name'] for service in required_services]

        # TODO : can join PassportStudioAccess and MboService and get the studio access list at query level
        mbo_services = MboService.objects.filter(studio=mbo_client.studio, is_active=True, name__in=required_services_names)
        for mbo_service in mbo_services:
            studio_ids_dict = PassportStudioAccess.objects.get_accessible_studios_by_mbo_service(mbo_service)
            for studio_id_dict in studio_ids_dict:
                studio_access_list.add(studio_id_dict['studio'])

    studio_access_list.add(studio.id)

    return studio_access_list


def get_class_items(user, home_studio, date_of_class, page, page_count, lat=None, lng=None):

    studio_access_list = get_studio_access_list(user, home_studio)
    classes = SliceClass.objects.get_classes_by_date_and_studio(date_of_class, studio_access_list)
    total_classes = classes.count()
    if page is not None:
        classes = paginate(classes, page, page_count)
    class_item_list = []

    rows = venues_dao.get_studios_with_settings()
    studios_new = {}
    for row in rows:
        studios_new[row[0]] = row

    # Get the number of locations each studio has. It is used to display the location name. If the studio has more
    # than one location then format the location name displayed as "StudioName - LocationName".
    mbolocation_result = MBOLocation.objects.all().values('studio_id').annotate(num_location=Count('studio_id'))

    studio_location_count = {}
    for mbolocation in mbolocation_result:
        studio_location_count[mbolocation['studio_id']] = mbolocation['num_location']

    for slice_class in classes:
        class_item = {}
        populate_class_basic_info(class_item, slice_class)

        use_mbo_location = True
        studio = studios_new[slice_class.studio_id]
        # Element studio[2] contains the value of room_location_enabled flag.
        if studio[2]:
            handle_room_location(slice_class, class_item)
            use_mbo_location = False

        class_item['use_mbo_location'] = use_mbo_location

        if use_mbo_location:
            populate_class_studio_info(class_item, slice_class.studio)
            populate_class_location_info(class_item, slice_class.mbolocation.location)
            if studio_location_count[slice_class.studio_id] > 1:
                class_item['multilocation'] = True
            else:
                class_item['multilocation'] = False

        # Duration is in minutes
        class_item['duration'] = get_duration_in_minutes(slice_class)

        populate_class_staff_info(class_item, slice_class.staff)

        class_item['action'] = 'book'
        class_item_list.append(class_item)

    if not user.is_anonymous():
        from bookings.bookings_core.booking_manager import sync_client_bookings
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, home_studio)
        sync_client_bookings(mbo_client)
        bookings = Booking.objects.get_all_booking_by_mbo_client_and_date(mbo_client.id, date_of_class)
        for booking in bookings:
            for class_item in class_item_list:
                if class_item["id"] == booking.slice_class.id:
                    class_item['action'] = 'cancel'
                    populate_class_booking_info(class_item, booking)

                    if is_within_sign_in_period(class_item["start_date"], class_item["start_time"]):
                        if not booking.signed_in:
                            if lat and lng:
                                if class_item.pop("use_mbo_location", False):
                                    allow_sign_in = is_inside_radius(booking.slice_class.mbolocation.location.latitude,
                                                                 booking.slice_class.mbolocation.location.longitude,
                                                                 lat, lng)
                                    if allow_sign_in:
                                        class_item['action'] = 'sign_in'
                                elif ('latitude' in class_item['location']) and ('longitude' in class_item['location']):
                                    allow_sign_in = is_inside_radius(class_item['location']['latitude'],
                                                                     class_item['location']['longitude'], lat, lng)
                                    if allow_sign_in:
                                        class_item['action'] = 'sign_in'
                        elif booking.signed_in:
                            class_item['action'] = 'arrived'

    if page is not None:
        classes_response = {}
        classes_response.setdefault('classes', class_item_list)
        populate_paginator_info(classes_response, total_classes, page, page_count)
        return classes_response

    return class_item_list


def get_class_item(slice_class, user, home_studio=None,  lat=None, lng=None):
    class_item = {}

    populate_class_basic_info(class_item, slice_class)
    if slice_class.schedule:
        populate_schedule_info(class_item, slice_class.schedule)

    studio = slice_class.studio

    studio_setting = StudioSettings.objects.get_studio_settings_by_studio_id(studio.id)

    use_mbo_location = True
    if studio_setting.room_location_enabled:
        if slice_class.mbo_resource_id:
            room_location = RoomLocation.objects.get_room_location_by_mbo_resource_id(slice_class.mbo_resource_id)
            if room_location:
                populate_class_location_info(class_item, room_location.location)
                populate_class_studio_info(class_item, room_location.studio)
                class_item['multilocation'] = True
            else:
                populate_class_location_info(class_item=class_item, default=True)
                populate_class_studio_info(class_item, studio)
                class_item['multilocation'] = False
            use_mbo_location = False
        else:
            populate_class_location_info(class_item=class_item, default=True)
            populate_class_studio_info(class_item, studio)
            class_item['multilocation'] = False
            use_mbo_location = False

    if use_mbo_location:
        populate_class_studio_info(class_item, studio)
        populate_class_location_info(class_item, slice_class.mbolocation.location)
        mbo_location_count = MBOLocation.objects.get_mbolocation_count_by_studio_id(studio.id)
        if mbo_location_count > 1:
            class_item['multilocation'] = True
        else:
            class_item['multilocation'] = False

    # Duration is in minutes
    class_item['duration'] = get_duration_in_minutes(slice_class)

    class_item['action'] = 'book'

    if not user.is_anonymous():
        from bookings.bookings_core.booking_manager import sync_client_bookings
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, home_studio)
        sync_client_bookings(mbo_client)
        booking = Booking.objects.get_booking_by_mbo_client_and_class(mbo_client_id=mbo_client.id, slice_class_id=slice_class.id)
        if booking:
            class_item['action'] = 'cancel'
            populate_class_booking_info(class_item, booking)

            if is_within_sign_in_period(class_item["start_date"], class_item["start_time"]):
                if not booking.signed_in:
                    if lat and lng:
                        if use_mbo_location:
                            allow_sign_in = is_inside_radius(booking.slice_class.mbolocation.location.latitude,
                                                             booking.slice_class.mbolocation.location.longitude,
                                                             lat, lng)
                            if allow_sign_in:
                                class_item['action'] = 'sign_in'
                        elif ('latitude' in class_item['location']) and ('longitude' in class_item['location']):
                            allow_sign_in = is_inside_radius(class_item['location']['latitude'],
                                                             class_item['location']['longitude'], lat, lng)
                            if allow_sign_in:
                                class_item['action'] = 'sign_in'
                elif booking.signed_in:
                    class_item['action'] = 'arrived'

    populate_class_staff_info(class_item, slice_class.staff)

    return class_item


def populate_class_basic_info(class_item, slice_class):
    class_item['id'] = slice_class.id
    class_item["name"] = slice_class.name
    class_item["bookable"] = slice_class.bookable
    class_item["start_date"] = slice_class.start_date
    class_item["end_date"] = slice_class.end_date
    class_item["start_time"] = slice_class.start_time
    class_item["end_time"] = slice_class.end_time
    if slice_class.level:
        class_item["level"] = slice_class.level
    if slice_class.description:
        class_item["description"] = slice_class.description


def populate_class_staff_info(class_item, staff):
    staff_dict = {}
    staff_dict["id"] = staff.id
    staff_dict["first_name"] = staff.first_name
    staff_dict["last_name"] = staff.last_name
    staff_dict["name"] = staff.name
    staff_dict["is_male"] = staff.is_male
    class_item["staff"] = staff_dict


def populate_class_studio_info(class_item, studio):
    studio_dict = {}
    studio_dict['id'] = studio.id
    studio_dict['name'] = studio.name
    studio_dict['description'] = studio.description
    studio_dict['image'] = studio.image.url
    studio_dict['logo'] = studio.logo.url

    class_item['studio'] = studio_dict


def populate_class_location_info(class_item, location=None, default=False):
    location_dict = {}
    if not default:
        location_dict["name"] = location.name
        location_dict["city"] = location.city
        location_dict['latitude'] = location.latitude
        location_dict['longitude'] = location.longitude
        location_dict['postcode'] = location.postcode
        location_dict['address_line_1'] = location.address_line_1
        # TODO: This is not necessary. This is added to support Sandbox.
        if location.nearest_rail_station:
            location_dict['nearest_rail_station'] = location.nearest_rail_station.name
        else:
            location_dict['nearest_rail_station'] = "London"
    else:
        location_dict['nearest_rail_station'] = "London"
    class_item["location"] = location_dict


def populate_class_booking_info(class_item, booking):
    user_booking = {}
    user_booking["id"] = booking.id
    user_booking["is_cancelled"] = booking.is_cancelled
    user_booking["is_confirmed"] = booking.is_confirmed
    user_booking["signed_in"] = booking.signed_in
    class_item["booking"] = user_booking


def get_duration_in_minutes(slice_class):
    duration = dateutil.time_diff(slice_class.end_time, slice_class.start_time)
    return duration.seconds / 60


# Todo : change argument name class_item to just item, because item can be a booking item or class item
def handle_room_location(slice_class, class_item):
    # Here item can be either class item or booking item.
    if slice_class.mbo_resource_id:
        room_location = RoomLocation.objects.get_room_location_by_mbo_resource_id(slice_class.mbo_resource_id)
        if room_location:
            populate_class_location_info(class_item, room_location.location)
            populate_class_studio_info(class_item, room_location.studio)
            class_item['multilocation'] = True
            return

    populate_class_location_info(class_item=class_item, default=True)
    populate_class_studio_info(class_item, slice_class.studio)
    class_item['multilocation'] = False


def handle_session_type_update(session_type, mbo_session_type):
    logger.debug("Entered handle_session_type_update (slice_session_type_id: {}, mbo_session_type_id: {})".
                 format(session_type.id, mbo_session_type.ID))
    update_required = False
    if session_type.name != mbo_session_type.Name:
        session_type.name = mbo_session_type.Name
        update_required = True

    if session_type.program_id != mbo_session_type.ProgramID:
        session_type.program_id = mbo_session_type.ProgramID
        update_required = True

    if session_type.num_deducted != mbo_session_type.NumDeducted:
        session_type.num_deducted = mbo_session_type.NumDeducted
        update_required = True

    if update_required:
        session_type.save()
        logger.info("Session type updated (slice_session_type_id: {}, mbo_session_type_id: {}".
                    format(session_type.id, mbo_session_type.ID))
    logger.debug("Leaving handle_session_type.")


def handle_schedule_from_mbo(mbo_schedule, mbo_site_id):
    studio = Studio.objects.get_studio_by_mbo_site_id(mbo_site_id)

    schedule_attrs = ['day_sunday', 'day_monday', 'day_tuesday', 'day_wednesday', 'day_thursday', 'day_friday', 'day_saturday', 'start_date', 'end_date', 'start_time', 'end_time']
    mbo_schedule_attrs = ['DaySunday', 'DayMonday', 'DayTuesday', 'DayWednesday', 'DayThursday', 'DayFriday', 'DaySaturday', 'StartDate', 'EndDate', 'StartTime', 'EndTime']
    schedule = Schedule.objects.get_schedule_by_mbo_schedule_id_and_studio(mbo_schedule.ID, studio.id)
    if schedule:
        logger.debug("Entered update schedule (schedule id: {})".format(schedule.id))

        updated = False

        for index, attr in enumerate(schedule_attrs):
            if getattr(schedule, attr) != getattr(mbo_schedule, mbo_schedule_attrs[index]):
                setattr(schedule, attr, getattr(mbo_schedule, mbo_schedule_attrs[index]))
                updated = True

        if updated:
            schedule.save()
        logger.info("Updated schedule (schedule id: {})".format(schedule.id))
    else:
        schedule = Schedule()
        schedule.mbo_schedule_id = mbo_schedule.ID
        schedule.studio = studio

        for index, attr in enumerate(schedule_attrs):
            setattr(schedule, attr, getattr(mbo_schedule, mbo_schedule_attrs[index]))
        schedule.save()

        logger.info("Created schedule (schedule id: {})".format(schedule.id))
    logger.debug("Leaving handle_schedule_from_mbo.")


def populate_schedule_info(class_item, schedule):
    class_schedule = {}
    class_schedule["id"] = schedule.id
    class_schedule["sun"] = schedule.day_sunday
    class_schedule["mon"] = schedule.day_monday
    class_schedule["tue"] = schedule.day_tuesday
    class_schedule["wed"] = schedule.day_wednesday
    class_schedule["thu"] = schedule.day_thursday
    class_schedule["fri"] = schedule.day_friday
    class_schedule["sat"] = schedule.day_saturday
    class_item["schedule"] = class_schedule


def assign_values_to_schedule(schedule, sunday, monday, tuesday, wednesday, thursday, friday, saturday, start_date, end_date, start_time, end_time):
    schedule.day_sunday = sunday
    schedule.day_monday = monday
    schedule.day_tuesday = tuesday
    schedule.day_wednesday = wednesday
    schedule.day_thursday = thursday
    schedule.day_friday = friday
    schedule.day_saturday = saturday
    schedule.start_date = start_date
    schedule.end_date = end_date
    schedule.start_time = start_time
    schedule.end_time = end_time


def get_class_list_by_studio(date, studio_id):
    class_lists = SliceClass.objects.get_all_classes_by_date_and_studio(date, studio_access_list=[studio_id])
    class_item_list = []
    for slice_class in class_lists:
        class_item = {}
        populate_class_basic_info(class_item, slice_class)
        populate_cancellation_info(class_item, slice_class)
        populate_class_staff_info(class_item, slice_class.staff)
        class_item_list.append(class_item)
    return class_item_list


def cancel_a_class_and_send_email_to_clients(class_id):
    slice_class = SliceClass.objects.get_class_by_id(class_id)
    bookings = Booking.objects.get_bookings_users_by_class(slice_class.id)
    for booking in bookings:
        booking.cancel()

        if booking.slice_class.studio != booking.mbo_client.studio:
            send_class_cancellation_emails(booking, slice_class, dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London"))

    slice_class.is_cancelled = True
    slice_class.save()
    logger.info("Cancelled class with id {}".format(class_id))


def populate_cancellation_info(class_item, slice_class):

    if not slice_class.bookable or slice_class.is_cancelled:
        class_item['cancellation'] = False
    else:
        class_item['cancellation'] = True


def get_class_status(class_id):
    slice_class = SliceClass.objects.get_class_by_id(class_id)
    mbo_class = MboGetClass(slice_class.studio.mbo_site_id, slice_class.mbo_class_id, slice_class.start_date,
                            slice_class.end_date)

    if mbo_class.response and mbo_class.response.Classes[0][0]:
        return mbo_class.response.Classes[0][0].IsCanceled


def paginate(query_result, page, page_count):
        if page:
            start = (page - 1) * page_count
            end = start + page_count
            query = query_result[start:end]
        else:
            query = query_result[:page_count]

        return query


def populate_paginator_info(response_item, total_classes, page, page_count):
    response_item.setdefault('total', total_classes)
    response_item.setdefault('page', page)
    response_item.setdefault('pageCount', page_count)


def handle_class_deactivation(synced_class_ids, current_class_ids):
    diff_ids = list(set(current_class_ids) - set(synced_class_ids))
    slice_classes = SliceClass.objects.get_classes_by_studio_ids(diff_ids)
    for slice_class in slice_classes:
        slice_class.is_active = False
        slice_class.save()
