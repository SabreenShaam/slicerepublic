from mind_body_online.SaleService import SaleServiceCalls
from django.core.exceptions import ValidationError
from services.exceptions import CreditCardNumberAuthorizationException, CreditCardCommonException
from slicerepublic.exceptions import InternalServerError
import logging

logger = logging.getLogger(__name__)


def checkout_complimentary_shopping_cart_item(mbo_client_id, mbo_service_id, mbo_site_id, staff_username, staff_password):

    sale_service = SaleServiceCalls()
    item_type_service = sale_service.CreateAbstractObject("Service", {"ID": mbo_service_id})
    cart_item = sale_service.CreateCartItem(arrayToFill=None, item=item_type_service)
    complimentary_payment_info = sale_service.CreateAbstractObject("CompInfo", {"Amount": 0})
    response = sale_service.CheckoutShoppingCart(
        clientId=mbo_client_id,
        cartItems=[cart_item],
        payments=[complimentary_payment_info],
        mbo_site_ids=[mbo_site_id],
        mbo_username=staff_username,
        mbo_password=staff_password
    )

    if response.Status != "Success":
        message = None
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response status : {} Response Message: {}".format(response.Status, message))

        if not message:
             logger.error("Response status : {}".format(response.Status))

        raise ValidationError("Failed checkout complimentary shopping cart item!")
    return response


def get_all_mbo_sales_services(mbo_site_id, program_ids):
    sale_service = SaleServiceCalls()
    response = sale_service.GetServices(
        programIds=[program_ids],
        site_ids=[mbo_site_id],
        sellOnline=True,
        hideRelatedPrograms=False,
    )
    if response.Status != "Success":
        logger.error("Response status : {}".format(response.Status))
        raise ValidationError("Failed to retrieve services!")

    return response


def checkout_credit_cart_item(mbo_client_id, mbo_service_id, amount, mbo_site_id, card_number, exp_year, exp_month, billing_name, staff_username, staff_password, is_test):
    sale_service = SaleServiceCalls()
    item_type_service = sale_service.CreateAbstractObject("Service", {"ID": mbo_service_id})
    action_code = sale_service.CreateAbstractObject("ActionCode", {'None': 'None'})
    cart_item = sale_service.CreateCartItem(arrayToFill=None, item=item_type_service, action=action_code)

    credit_card_info = {"Amount": amount,
                        "CreditCardNumber": card_number,
                        "ExpYear": exp_year,
                        "ExpMonth": exp_month,
                        "BillingName": billing_name,
                        }

    payment_info = sale_service.CreateAbstractObject("CreditCardInfo", credit_card_info)

    delattr(payment_info, 'Action')
    response = sale_service.CheckoutShoppingCart(
        clientId=mbo_client_id,
        cartItems=[cart_item],
        payments=[payment_info],
        mbo_site_ids=[mbo_site_id],
        mbo_username=staff_username,
        mbo_password=staff_password,
        test=is_test
    )

    if response.Status != "Success":
        if response.ErrorCode == 900:
            message = None
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))

                if "Card Authorization Failed" in message:
                    raise CreditCardNumberAuthorizationException("50100", "Card Authorization Failed", "Card Authorization Failed. Please check your credit card number")
                else:
                    raise CreditCardCommonException("50200", "Problem encountered with credit card details", "Problem encountered to continue the process. Please contact your home studio.")

            if not message:
                 logger.error("Response status : {}".format(response.Status))

        raise InternalServerError("10100", "Internal Error", "Internal Service Error")

    return response


def get_summary_for_service_item(mbo_client_id, mbo_service_id, mbo_site_id, is_test):
    sale_service = SaleServiceCalls()
    item_type_service = sale_service.CreateAbstractObject("Service", {"ID": mbo_service_id})
    cart_item = sale_service.CreateCartItem(arrayToFill=None, item=item_type_service)

    response = sale_service.CheckoutShoppingCart(
        clientId=mbo_client_id,
        cartItems=[cart_item],
        mbo_site_ids=[mbo_site_id],
        inStore=True,
        fieldname="paymentcheck",
        test=is_test,
    )

    if response.Status != "Success":
        message = None
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response status : {} Response Message: {}".format(response.Status, message))
        if not message:
             logger.error("Response status : {}".format(response.Status))

        if response.ErrorCode == 905:
            raise InternalServerError("10000", "Service Failed", "We are unable to sell this service to you!")
        else:
            raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


def checkout_cart_item_with_stored_credit_card(mbo_client_id, mbo_service_id, mbo_site_id, amount, last_four, staff_username, staff_password, is_test):
    sale_service = SaleServiceCalls()
    item_type_service = sale_service.CreateAbstractObject("Service", {"ID": mbo_service_id})
    cart_item = sale_service.CreateCartItem(arrayToFill=None, item=item_type_service)
    payment_info = sale_service.CreateAbstractObject("StoredCardInfo", {"Amount": amount, "LastFour": last_four})
    response = sale_service.CheckoutShoppingCart(
        clientId=mbo_client_id,
        cartItems=[cart_item],
        payments=[payment_info],
        mbo_site_ids=[mbo_site_id],
        mbo_username=staff_username,
        mbo_password=staff_password,
        test=is_test,
    )

    if response.Status != "Success":
        logger.error("CheckoutShoppingCart soap request failed")
        if response.ErrorCode == 900:
            message = None
            if hasattr(response, 'Message'):
                message = response.Message
                logger.error("Response status : {} Response Message: {}".format(response.Status, message))
                if "Card Authorization Failed" in message:
                    raise CreditCardNumberAuthorizationException("50100", "Card Authorization Failed", "Card Authorization Failed. Please check your credit card number")
                else:
                    raise CreditCardCommonException("50200", "Problem encountered with credit card details", "Problem encountered to continue the process. Please contact your home studio.")
            if not message:
                 logger.error("Response status : {}".format(response.Status))

        raise InternalServerError("10100", "Internal Error", "Internal Service Error")
    return response


def purchase_complementary_item_and_add_client_to_class(class_id, mbo_client_id, mbo_service_id, mbo_site_id, staff_username, staff_password):
    sale_service = SaleServiceCalls()

    item_type_service = sale_service.CreateAbstractObject("Service", {"ID": mbo_service_id})
    cart_item = sale_service.CreateCartItem(arrayToFill=None, item=item_type_service, classIds=[class_id])
    complimentary_payment_info = sale_service.CreateAbstractObject("CompInfo", {"Amount": 0})
    response = sale_service.CheckoutShoppingCart(
        clientId=mbo_client_id,
        cartItems=[cart_item],
        payments=[complimentary_payment_info],
        mbo_site_ids=[mbo_site_id],
        mbo_username=staff_username,
        mbo_password=staff_password,
        test=False
    )
    if response.Status != "Success":
        message = None
        if hasattr(response, 'Message'):
            message = response.Message
            logger.error("Response status : {} Response Message: {}".format(response.Status, message))

        if not message:
             logger.error("Response status : {}".format(response.Status))

        raise InternalServerError("10100", "Internal Error", "Failed checkout complimentary shopping cart item!")
    return response
