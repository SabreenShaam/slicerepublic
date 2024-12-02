from model_mommy.recipe import Recipe, foreign_key

from accounts.mommy_recipes import mbo_client
from bookings.bookings_core.models import Booking, ExternalBookingService, UnpaidBookings
from classes.mommy_recipes import slice_class_external, slice_class
from services.mommy_recipes import mbo_client_service


booking = Recipe(
    Booking,
    slice_class=foreign_key(slice_class),
    created='2015-06-28',
    mbo_visit_id=25,
    mbo_client=foreign_key(mbo_client),
)

booking_external = Recipe(
    Booking,
    slice_class=foreign_key(slice_class_external),
    created='2015-06-28',
    mbo_visit_id=25,
    mbo_client=foreign_key(mbo_client),
)

booking_external1 = Recipe(
    Booking,
    slice_class=foreign_key(slice_class_external),
    created='2015-06-28',
    mbo_visit_id=25,
    mbo_client=foreign_key(mbo_client),
)

booking_external3 = Recipe(
    Booking,
    slice_class=foreign_key(slice_class_external),
    created='2015-06-28',
    mbo_visit_id=25,
    mbo_client=foreign_key(mbo_client),
)

# external_booking_service1 = Recipe(
#     ExternalBookingService,
#     booking=foreign_key(booking_external1),
#     mbo_client_service=foreign_key(mbo_client_service_2),
# )
#
# external_booking_service3 = Recipe(
#     ExternalBookingService,
#     booking=foreign_key(booking_external3),
#     mbo_client_service=foreign_key(mbo_client_service_2),
# )

booking_external2 = Recipe(
    Booking,
    slice_class=foreign_key(slice_class_external),
    created='2015-06-30',
    mbo_visit_id=25,
    mbo_client=foreign_key(mbo_client),
)


external_booking_service2 = Recipe(
    ExternalBookingService,
    booking=foreign_key(booking_external2),
    mbo_client_service=foreign_key(mbo_client_service),
)

unpaid_booking = Recipe(
    UnpaidBookings,
    booking=foreign_key(booking_external),
    is_paid=False,
    parent_service=foreign_key(mbo_client_service)

)

# unpaid_booking2 = Recipe(
#     UnpaidBookings,
#     booking=foreign_key(booking_external1),
#     is_paid=False,
#     parent_service=foreign_key(mbo_client_service_2)
# )
#
# unpaid_booking3 = Recipe(
#     UnpaidBookings,
#     booking=foreign_key(booking_external3),
#     is_paid=False,
#     parent_service=foreign_key(mbo_client_service_3)
# )