from django.db.models import Q
from accounts.models import MboClient
from bookings.bookings_core.models import ExternalBookingService
from mind_body_service import client_api
from services.models import MboService, MboClientService, StudioService, ShoppingCart, ClientCreditCardInfo, \
    PassportStudioAccess
from classes.models import Program
from datetime import timedelta

from mind_body_service.client_api import get_client_services
from mind_body_service.site_api import get_programs
from mind_body_service.sale_api import get_all_mbo_sales_services, checkout_credit_cart_item, \
    get_summary_for_service_item, checkout_cart_item_with_stored_credit_card

from classes.class_mapper import map_values_from_mbo_program_to_program

from services.service_mapper import map_values_from_service_to_mbo_client_service, \
    map_values_from_mbo_studio_service_to_studio_service

from slicerepublic import dateutil
from slicerepublic.dateutil import utcnow
from django.conf import settings
from django.core.cache import cache

import logging
from venues.models import Studio
from venues.venues_util import calculate_drop_in_transfer_price, calculate_ten_pack_transfer_price, \
    calculate_transfer_price

logger = logging.getLogger(__name__)


def sync_mbo_client_services(mbo_client):
    mbo_program_ids_result = Program.objects.get_integrated_program_id_list_by_studio(mbo_client.studio)
    mbo_program_ids = [entry for entry in mbo_program_ids_result]
    start_date = dateutil.utcnow_plus(timedelta(days=-settings.CLIENT_SERVICES_TIMEDELTA_INTERVAL))
    end_date = dateutil.utcnow_plus(timedelta(days=settings.CLIENT_SERVICES_TIMEDELTA_INTERVAL))
    mbo_services = get_client_services_program_by_program(mbo_client.mbo_client_id, mbo_client.studio.mbo_site_id,
                                                          mbo_program_ids, start_date, end_date, False)
    mbo_client_services = MboClientService.objects.filter(mbo_client=mbo_client)

    if len(mbo_services) == 0:
        for mbo_client_service in mbo_client_services:
            mbo_client_service.current = False
            mbo_client_service.save()
        return

    if not mbo_client_services:
        for service in mbo_services:
            create_new_mbo_client_service(service, mbo_client)
    else:
        for service in mbo_services:
            updated = False
            for mbo_client_service in mbo_client_services:
                if mbo_client_service.mbo_client_service_id == service.ID:
                    update_mbo_client_service(service, mbo_client_service)
                    logger.info("Updated MboClientService (serivce id : {})".format(service.ID))
                    updated = True
                    break
            if not updated:
                create_new_mbo_client_service(service, mbo_client)

        for mbo_client_service in mbo_client_services:
            found = False
            for service in mbo_services:
                if mbo_client_service.mbo_client_service_id == service.ID:
                    found = True

            if not found:
                mbo_client_service.current = False
                mbo_client_service.save()


def get_client_services_program_by_program(mbo_client_id, mbo_site_id, mbo_program_ids, start_date, end_date,
                                           show_active_only):
    logger.debug("Syncing client services program by program")
    mbo_service_ids = []
    mbo_services = []
    for mbo_program_id in mbo_program_ids:
        services = get_client_services(mbo_client_id, [mbo_program_id], mbo_site_id, start_date, end_date,
                                       show_active_only)
        if services.ResultCount > 0:
            for service in services.ClientServices.ClientService:
                if service.ID not in mbo_service_ids:
                    mbo_service_ids.append(service.ID)
                    mbo_services.append(service)
    logger.debug("Sync completed")
    return mbo_services


def update_mbo_client_service(service, mbo_client_service):
    mbo_client_service = map_values_from_service_to_mbo_client_service(service, mbo_client_service)
    mbo_client_service.last_sync_date = utcnow()
    mbo_client_service.save()


def create_new_mbo_client_service(service, mbo_client):
    program = Program.objects.get_program_by_mbo_program_id_and_studio(service.Program.ID, mbo_client.studio)
    if not program:
        mbo_programs = get_programs(mbo_client.studio.mbo_site_id)
        logger.debug(
            "Program with id {} in studio {} does not exists!".format(service.Program.ID, mbo_client.studio.name))
        for mbo_program in mbo_programs:
            if mbo_program.ID == service.Program.ID:
                program = create_new_program_from_mbo_program(mbo_program, mbo_client.studio)
                break
        if program is None:
            logger.error("MBO Program with id {} in studio {} does not exists!".format(service.Program.ID,
                                                                                       mbo_client.studio.name))
            return

    mbo_client_service = MboClientService()
    mbo_client_service.name = service.Name
    mbo_client_service.mbo_client = mbo_client
    mbo_client_service.mbo_client_service_id = service.ID

    map_values_from_service_to_mbo_client_service(service, mbo_client_service)

    mbo_client_service.program = program
    mbo_client_service.last_sync_date = utcnow()
    mbo_client_service.save()
    logger.info("Created MboClientService (service id : {})".format(service.ID))
    return mbo_client_service


def get_all_client_services(mbo_client):
    mbo_client_service_items = []
    logger.debug("Entered get all client services [mbo_client_id: {}]".format(mbo_client.id))
    local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    mbo_client_services = MboClientService.objects.filter(Q(expiration_date__gte=local_dt), mbo_client=mbo_client)
    for mbo_client_service in mbo_client_services:
        if not mbo_client_service.current and mbo_client_service.remaining == 0:
            mbo_client_service_items.append(mbo_client_service)
        elif mbo_client_service.current:
            mbo_client_service_items.append(mbo_client_service)
    logger.debug("Leaving get all client service")
    return mbo_client_service_items


def get_required_services_for_external_bookings(mbo_client):
    service_items = []
    logger.info("Entered has_unexpired required service.")
    local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    mbo_client_services = MboClientService.objects.filter(Q(expiration_date__gte=local_dt),
                                                          Q(current=True) | Q(current=False, remaining=0),
                                                          mbo_client=mbo_client,
                                                          name__in=MboService.objects.filter(studio=mbo_client.studio,
                                                                                             is_active=True).values_list(
                                                              'name', flat=True))
    logger.info("User with mbo client id {} in studio {} having client service item!".format(mbo_client.mbo_client_id,
                                                                                             mbo_client.studio))
    for mbo_client_service in mbo_client_services:
        service_item = populate_client_service_item(mbo_client_service)
        service_items.append(service_item)
    return service_items


def populate_client_service_item(mbo_client_service):
    service_item = {}
    service_item['id'] = mbo_client_service.id
    service_item['name'] = mbo_client_service.name
    service_item['count'] = mbo_client_service.count
    service_item['remaining'] = mbo_client_service.remaining
    service_item['expire_date'] = mbo_client_service.expiration_date
    service_item['active_date'] = mbo_client_service.active_date
    return service_item


def create_new_program_from_mbo_program(mbo_program, studio):
    program = map_values_from_mbo_program_to_program(mbo_program)
    program.opens = 14
    program.is_integrated = False
    program.site = studio
    program.save()
    logger.debug("Created mbo program with id {} for studio {}".format(mbo_program.ID, studio.name))
    return program


def get_studio_service_list(studio):
    logger.debug('Entered studio service list for studio : {}'.format(studio.id))

    if not cache.get('key_sync_studio_services_' + str(studio.id)):
        logger.info('Synchronizing services of studio {}'.format(studio.name))
        sync_studio_services(studio)
        cache.set('key_sync_studio_services_' + str(studio.id), "Synced", settings.STUDIO_SERVICES_SYNC_TIMEOUT)

    services = StudioService.objects.get_studio_services_by_studio(studio)
    logger.debug('Number of services : {}'.format(len(services)))
    return services


def sync_studio_services(studio):
    program_ids = list(Program.objects.get_integrated_program_id_list_by_studio(studio))

    if len(program_ids) == 0:
        logger.error("No program ids found for studio {}".format(studio.name))
        return

    slice_studio_services = StudioService.objects.get_studio_services_by_studio(studio)
    mbo_studio_services = get_all_mbo_sales_services(studio.mbo_site_id, program_ids)

    if mbo_studio_services.ResultCount != 0:
        for mbo_studio_service in mbo_studio_services.Services.Service:  # check whether any items updated
            is_new = True
            for slice_studio_service in slice_studio_services:
                if slice_studio_service.mbo_service_id == int(mbo_studio_service.ID):
                    is_new = False
                    break

            if is_new:
                create_new_mbo_studio_service(mbo_studio_service, studio)
            else:
                if is_update_required(mbo_studio_service, slice_studio_service):
                    slice_studio_service.save()

        for slice_studio_service in slice_studio_services:  # check whether all items are still exist or not
            is_exist = False
            for mbo_studio_service in mbo_studio_services.Services.Service:
                if slice_studio_service.mbo_service_id == int(mbo_studio_service.ID):
                    is_exist = True
                    break
            if not is_exist:
                slice_studio_service.is_active = False  # make studio service item as inactive if not exist in mbo response
                slice_studio_service.save()
    elif mbo_studio_services.ResultCount == 0:
        for slice_studio_service in slice_studio_services:
            slice_studio_service.is_active = False  # make studio service item as inactive if not exist in mbo response
            slice_studio_service.save()


def create_new_mbo_studio_service(mbo_studio_service, studio):
    studio_service = StudioService()
    studio_service.studio = studio
    map_values_from_mbo_studio_service_to_studio_service(mbo_studio_service, studio_service)
    studio_service.save()


def is_update_required(mbo_studio_service, slice_studio_service):
    is_update = False
    if slice_studio_service.name != mbo_studio_service.Name:
        slice_studio_service.name = mbo_studio_service.Name
        is_update = True
    if slice_studio_service.mbo_product_id != mbo_studio_service.ProductID:
        slice_studio_service.mbo_product_id = mbo_studio_service.ProductID
        is_update = True
    if slice_studio_service.price != mbo_studio_service.Price:
        slice_studio_service.price = mbo_studio_service.Price
        is_update = True
    if slice_studio_service.online_price != mbo_studio_service.OnlinePrice:
        slice_studio_service.online_price = mbo_studio_service.OnlinePrice
        is_update = True
    if slice_studio_service.tax_rate != mbo_studio_service.TaxRate:
        slice_studio_service.tax_rate = mbo_studio_service.TaxRate
        is_update = True
    if slice_studio_service.count != mbo_studio_service.Count:
        slice_studio_service.count = mbo_studio_service.Count
        is_update = True
    if not slice_studio_service.is_active:
        slice_studio_service.is_active = True
        is_update = True

    return is_update


def checkout_shopping_cart(user, studio, studio_service, name, card_number, expiration_year, expiration_month):
    logger.debug("Entered checkout shopping cart")
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)

    mbo_site_id = mbo_client.studio.mbo_site_id
    mbo_service_id = studio_service.mbo_service_id

    is_test = settings.CREDIT_CARD_CHECKOUT_TEST

    response = get_summary_for_service_item(mbo_client.mbo_client_id, mbo_service_id, mbo_site_id, is_test)
    payment_amount = response.ShoppingCart.GrandTotal
    checkout_response = checkout_credit_cart_item(mbo_client.mbo_client_id,
                                                  mbo_service_id,
                                                  payment_amount,
                                                  mbo_site_id,
                                                  card_number,
                                                  expiration_year,
                                                  expiration_month,
                                                  name,
                                                  settings.MBO_STAFF_USERNAME,
                                                  settings.MBO_STAFF_PASSWORD,
                                                  is_test)

    save_shopping_cart_item(user, studio_service)

    logger.debug("Leaving checkout shopping cart")
    return checkout_response


def save_shopping_cart_item(user, cart_item):
    shopping_cart = ShoppingCart()
    shopping_cart.user = user
    shopping_cart.studio_service = cart_item
    shopping_cart.save()


def get_checkout_summary(user, studio, cart_item):
    logger.debug("Entered get checkout summary")
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)

    mbo_site_id = mbo_client.studio.mbo_site_id
    mbo_service_id = cart_item.mbo_service_id
    is_test = settings.CREDIT_CARD_CHECKOUT_TEST
    response = get_summary_for_service_item(mbo_client.mbo_client_id, mbo_service_id, mbo_site_id, is_test)
    service_summary_item = populate_service_summary_item_info(response.ShoppingCart)

    logger.debug("Leaving get checkout summary")
    return service_summary_item


def populate_service_summary_item_info(mbo_cart_item):
    service_item = {}
    service_item["grand_total"] = mbo_cart_item.GrandTotal
    service_item["tax_total"] = mbo_cart_item.TaxTotal
    service_item["sub_total"] = mbo_cart_item.SubTotal
    return service_item


def get_client_credit_card(user, studio):
    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)
    response = client_api.get_client(mbo_client.mbo_client_id, mbo_client.studio.mbo_site_id)

    credit_card = ClientCreditCardInfo.objects.get_client_credit_card_info_by_mbo_client(mbo_client.id)

    if not hasattr(response.Clients.Client[0], 'ClientCreditCard') or \
            not hasattr(response.Clients.Client[0].ClientCreditCard, 'CardType'):
        sync_credit_card_info(mbo_client, None, credit_card)
        credit_card = None
    else:
        mbo_credit_card = response.Clients.Client[0].ClientCreditCard
        sync_credit_card_info(mbo_client, mbo_credit_card, credit_card)
        credit_card = ClientCreditCardInfo.objects.get_client_credit_card_info_by_mbo_client(mbo_client.id)

    return credit_card


def sync_credit_card_info(mbo_client, mbo_credit_card, credit_card):
    if not credit_card and not mbo_credit_card:
        return
    elif credit_card and not mbo_credit_card:
        credit_card.is_active = False
        credit_card.save()
    elif not credit_card and mbo_credit_card:
        create_new_credit_card_info(mbo_client, mbo_credit_card)
    elif is_update_credit_card_info(credit_card, mbo_credit_card):
        credit_card.is_active = False
        credit_card.save()
        create_new_credit_card_info(mbo_client, mbo_credit_card)
        logger.debug("Credit card updated for {}, previous card number ****{}".format(mbo_client.user.email,
                                                                                      credit_card.last_four))


def is_update_credit_card_info(credit_card, mbo_credit_card):
    is_update = False

    if credit_card.last_four != int(mbo_credit_card.LastFour):
        is_update = True

    return is_update


def create_new_credit_card_info(mbo_client, credit_card_info):
    credit_card = ClientCreditCardInfo()
    credit_card.mbo_client = mbo_client
    credit_card.type = credit_card_info.CardType
    credit_card.last_four = credit_card_info.LastFour
    credit_card.exp_month = credit_card_info.ExpMonth
    credit_card.exp_year = credit_card_info.ExpYear

    if hasattr(credit_card_info, 'PostalCode'):
        credit_card.postal_code = credit_card_info.PostalCode

    credit_card.save()
    logger.debug(
        "Created new credit card info for {}, number ****{}".format(mbo_client.user.email, credit_card_info.LastFour))


def checked_cart_item_for_stored_credit_card(user, studio, studio_service_id):
    logger.debug("Entered checkout with stored credit card")

    mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)
    studio_service = StudioService.objects.get_studio_service_by_id(studio_service_id)
    mbo_site_id = mbo_client.studio.mbo_site_id
    mbo_service_id = studio_service.mbo_service_id
    credit_card = ClientCreditCardInfo.objects.get_client_credit_card_info_by_mbo_client(mbo_client.id)

    is_test = settings.CREDIT_CARD_CHECKOUT_TEST
    response = get_summary_for_service_item(mbo_client.mbo_client_id, mbo_service_id, mbo_site_id, is_test)
    payment_amount = response.ShoppingCart.GrandTotal

    checkout_response = checkout_cart_item_with_stored_credit_card(mbo_client.mbo_client_id, mbo_service_id,
                                                                   mbo_site_id, payment_amount, credit_card.last_four,
                                                                   settings.MBO_STAFF_USERNAME,
                                                                   settings.MBO_STAFF_PASSWORD, is_test)

    save_shopping_cart_item(user, studio_service)

    logger.debug("Leaving checkout credit card")
    return checkout_response


def client_services_sync(mbo_client):
    current_time = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
    count = 0

    if not cache.get('key_sync_client_services_' + str(mbo_client.id)):
        sync_mbo_client_services(mbo_client)
    else:
        value = cache.get('key_sync_client_services_' + str(mbo_client.id))
        count = value['count']
        time_interval = current_time - value['time']

        if time_interval.seconds < 5 * 60:
            sync_mbo_client_services(mbo_client)
        else:
            if count < 2:
                count += 1
            else:
                sync_mbo_client_services(mbo_client)
                count = 0

    cache_info = {'time': current_time, 'count': count}
    cache.set('key_sync_client_services_' + str(mbo_client.id), cache_info, settings.CLIENT_SERVICES_SYNC_TIMEOUT)


def create_or_update_mbo_service(service_id, studio_id, count, max_per_studio_count):
    mbo_service = MboService.objects.get_service_by_id_and_studio(service_id, studio_id)
    if mbo_service:
        mbo_service.count = count
        mbo_service.max_per_studio = max_per_studio_count
        mbo_service.save()
        logger.debug("Updated mbo service with name {}".format(service_id))


def update_mbo_service_state(service_id, studio_id, state):
    mbo_service = MboService.objects.get_service_by_id_and_studio(service_id, studio_id)
    mbo_service.change_state(state)
    logger.debug("Updated mbo service with name {}".format(service_id))


def get_mbo_services(studio_id):
    mbo_services_items = []
    studio = Studio.objects.get_studio_by_studio_id(studio_id)
    mbo_services = MboService.objects.get_mbo_services_by_studio(studio)
    populate_mbo_external_services(mbo_services, mbo_services_items)
    return mbo_services_items


def populate_mbo_external_services(mbo_services, mbo_services_items):
    for mbo_service in mbo_services:
        mbo_service_item = {}
        mbo_service_item['id'] = mbo_service.id
        mbo_service_item['count'] = mbo_service.count
        mbo_service_item['name'] = mbo_service.name
        mbo_service_item['max_per_studio'] = mbo_service.max_per_studio
        mbo_service_item['state'] = mbo_service.is_active
        mbo_services_items.append(mbo_service_item)


def settle_unpaid_bookings(unpaid_booking, mbo_client_service):
    logger.debug("unpaid booking id {}, Mbo service id {}".format(unpaid_booking.id, mbo_client_service.id))
    ExternalBookingService.objects.create_external_booking(unpaid_booking.booking, mbo_client_service)
    unpaid_booking.mark_as_paid()


def activate_auto_pay(user, studio, response):
    if response.ShoppingCart and response.ShoppingCart.CartItems[0][0]:
        mbo_client = MboClient.objects.get_mbo_client_by_studio_and_user(user, studio)
        sync_mbo_client_services(mbo_client)

        local_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
        service_item = response.ShoppingCart.CartItems[0][0]
        mbo_client_service = MboClientService.objects.get_active_new_mbo_client_service_by_names(mbo_client, local_dt,
                                                                                                 [service_item.Name],
                                                                                                 service_item.Count).first()
        if mbo_client_service:
            mbo_client_service.update_auto_pay(True)
            from services.pricing_option import PricingOption
            PricingOption.send_email(service_item.Name, user.email)
            PricingOption.send_email(service_item.Name, studio.email)
            logger.debug("Updated auto pay option for mbo_client_service".format(mbo_client_service.id))


def get_mbo_client_service_info(id):
    studio_service = MboClientService.objects.get_mbo_client_service_by_id(id=id)
    if studio_service and studio_service[0]:
        return studio_service[0].as_json()
    else:
        logger.debug("Mbo Client Service does not exist")
        return


def get_studio_access_by_mbo_service(mbo_service_id):
    passport_studio_access_list = PassportStudioAccess.objects.get_all_available_studios_by_mbo_service(mbo_service_id)
    return passport_studio_access_list


def update_passport_access(passport_studio_access_id, is_accessible_str):
    try:
        passport_studio_access = PassportStudioAccess.objects.get(id=passport_studio_access_id)
    except PassportStudioAccess.DoesNotExist:
        logger.error("PassportStudioAccess does not exist for id {}".format(passport_studio_access_id))

    is_accessible = True if is_accessible_str == 'true' else False
    passport_studio_access.update(is_accessible)

    logger.debug("PassportStudioAccess updated for id {}".format(passport_studio_access_id))


def populate_studio_access_list(pk):
    data = get_studio_access_by_mbo_service(pk)
    attributes = []
    for obj in data:
        dict = {}
        dict['id'] = obj.id
        price = calculate_price(obj.drop_in_price, obj.ten_pack_price)
        dict['studio'] = {'id': obj.studio_id, 'name': obj.name, 'price': price}
        dict['is_accessible'] = obj.is_accessible
        attributes.append(dict)
    return attributes


def calculate_price(drop_in_price, ten_pack_price):
    drop_in = calculate_drop_in_transfer_price(drop_in_price)
    ten_pack = calculate_ten_pack_transfer_price(ten_pack_price)
    transfer_price = calculate_transfer_price(drop_in, ten_pack)

    return transfer_price
