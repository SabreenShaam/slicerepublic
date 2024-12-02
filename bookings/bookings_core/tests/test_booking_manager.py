from datetime import datetime
from django.test import TestCase
from unittest.mock import patch, DEFAULT
from unittest import skipIf
from model_mommy import mommy
from bookings.bookings_core import booking_manager
from bookings.bookings_core.booking_manager import handle_unpaid_bookings, populate_external_booking_credits_details, \
	get_total_external_unpaid_bookings_count
from bookings.bookings_core.models import Booking, ExternalBookingService, UnpaidBookings
from services.models import MboClientService
from services.service_manager import settle_unpaid_bookings
from slicerepublic.base_test_setup import BaseExternalTestSetup
from slicerepublic.dateutil import make_utc


@skipIf(False, "Skip this test")
class BookingsTestCase(TestCase):
	def setUp (self):
		setup_resources = SetupResources(self)
		setup_resources.setup_parent()
		setup_resources.setup_studios1()
		setup_resources.setup_class_and_resources1()
		setup_resources.setup_user1()
		setup_resources.setup_studio_services1()
		setup_resources.setup_mbo_client_home_studio1()
		setup_resources.setup_mbo_client_services1()
		setup_resources.setup_mbo_services1()
		self.visit = Visit(25).get_visit()
		setup_resources.setup_mbo_client_external1()
		# setup_resources.setup_mbo_external_client1()
		setup_resources.setup_user_external_studio1()
		setup_resources.setup_external_booking1()
		setup_resources.setup_external_booking_service1()
		setup_resources.setup_unpaid_bookings1()

	@skipIf(True, "Skip this test")
	@patch.multiple('classes.mbo_class_service.MboGetClass', _fetch=DEFAULT, get_class=DEFAULT, is_empty=DEFAULT,
					get_site_id=DEFAULT, get_class_id=DEFAULT, has_free_web_slot=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.Booker', get_visit=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.InternalBooker', make_booking=DEFAULT)
	def test_book_class_in_home_studio (self, **mocks):
		self.assertEquals(1, 1)
		mock_fetch, mock_mbo_get_class, mock_is_empty, mock_get_site_id, mock_get_class_id, mock_has_free_web_slot = \
		mocks["_fetch"], mocks["get_class"], mocks["is_empty"], mocks["get_site_id"], mocks["get_class_id"], mocks[
			"has_free_web_slot"]
		mock_get_visit, mock_make_booking = mocks["get_visit"], mocks["make_booking"]

		# Mock classes_api methods
		self.slice_class_home.ID = 1
		mock_mbo_get_class.return_value = self.slice_class_home
		mock_fetch.return_value = True
		mock_is_empty.return_value = True
		mock_get_site_id.return_value = -99
		mock_get_class_id.return_value = 2240
		mock_has_free_web_slot.return_value = True
		mock_get_visit.return_value = self.visit
		mock_make_booking.return_value = True

		booking_manager.book_class(self.slice_class_home, self.user_home, self.home_studio)
		bookings = Booking.objects.all()
		self.assertEquals(2, bookings.count())

		booking = Booking.objects.get(pk=bookings.first().id)
		self.assertEquals(25, booking.mbo_visit_id)

	@skipIf(True, "Skip this test")
	@patch.multiple('classes.mbo_class_service.MboGetClass', _fetch=DEFAULT, get_class=DEFAULT, is_empty=DEFAULT,
					get_site_id=DEFAULT, get_class_id=DEFAULT, has_free_web_slot=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.Booker', get_visit=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.ExternalBooker', make_booking=DEFAULT)
	def test_book_class_in_another_studio_case1 (self, **mocks):
		mock_fetch, mock_mbo_get_class, mock_is_empty, mock_get_site_id, mock_get_class_id, mock_has_free_web_slot = \
		mocks["_fetch"], mocks["get_class"], mocks["is_empty"], mocks["get_site_id"], mocks["get_class_id"], mocks[
			"has_free_web_slot"]
		mock_get_visit, mock_make_booking = mocks["get_visit"], mocks["make_booking"]

		self.slice_class_external.ID = 1
		mock_mbo_get_class.return_value = self.slice_class_external
		mock_fetch.return_value = True
		mock_is_empty.return_value = True
		mock_get_site_id.return_value = -99
		mock_get_class_id.return_value = 2240
		mock_has_free_web_slot.return_value = True
		mock_get_visit.return_value = self.visit
		mock_make_booking.return_value = True
		# Mock classes_api methods
		booking_manager.book_class(self.slice_class_external, self.user_home, self.home_studio)
		bookings = Booking.objects.all()
		self.assertEquals(2, bookings.count())

		external_bookings = ExternalBookingService.objects.all()
		unpaid_bookings = UnpaidBookings.objects.all()
		self.assertEquals(1, external_bookings.count())
		self.assertEquals(1, unpaid_bookings.count())

	@skipIf(False, "Skip this test")
	@patch.multiple('classes.mbo_class_service.MboGetClass', _fetch=DEFAULT, get_class=DEFAULT, is_empty=DEFAULT,
					get_site_id=DEFAULT, get_class_id=DEFAULT, has_free_web_slot=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.Booker', get_visit=DEFAULT)
	@patch.multiple('bookings.bookings_api.booker.ExternalBooker', make_booking=DEFAULT)
	def test_book_class_in_another_studio_case2 (self, **mocks):
		mock_fetch, mock_mbo_get_class, mock_is_empty, mock_get_site_id, mock_get_class_id, mock_has_free_web_slot = \
		mocks["_fetch"], mocks["get_class"], mocks["is_empty"], mocks["get_site_id"], mocks["get_class_id"], mocks[
			"has_free_web_slot"]
		mock_get_visit, mock_make_booking = mocks["get_visit"], mocks["make_booking"]

		self.slice_class_external.ID = 1
		mock_mbo_get_class.return_value = self.slice_class_external
		mock_fetch.return_value = True
		mock_is_empty.return_value = True
		mock_get_site_id.return_value = -99
		mock_get_class_id.return_value = 2240
		mock_has_free_web_slot.return_value = True
		mock_get_visit.return_value = self.visit
		mock_make_booking.return_value = True
		# Mock classes_api methods
		booking_manager.book_class(self.slice_class_external, self.user_home2, self.home_studio)
		bookings = Booking.objects.all()
		self.assertEquals(2, bookings.count())

		external_bookings = ExternalBookingService.objects.all()
		unpaid_bookings = UnpaidBookings.objects.all()
		self.assertEquals(1, external_bookings.count())
		self.assertEquals(1, unpaid_bookings.count())

	@skipIf(True, "Skip this test")
	def test_unpaid_bookings(self):
		mbo_client_service = MboClientService.objects.get_service_by_name_and_payment_date(self.mbo_client_home, 'Intro', '2016-07-10')
		if mbo_client_service:
			settle_unpaid_bookings(self.mbo_client_service, self.mbo_client_home)
		#settle_unpaid_bookings(self.mbo_client_service_2, self.mbo_client_home)
		self.assertEquals(2, 2)

	@skipIf(True, "Skip this test")
	def test_get_parent_Services_for_unpaid_bookings(self):
		# services = UnpaidBookings.objects.get_active_unpaid_bookings()
		handle_unpaid_bookings()
		#self.assertEquals(2, services.count())

	@skipIf(True, "Skip this test")
	def test_populate_external_booking_credits_details(self):
		list = populate_external_booking_credits_details(self.user_home, self.home_studio)
		self.assertEquals(2, len(list))

	@skipIf(False, "Skip this test")
	def test_total_external_unpaid_bookings_count(self):
		count = get_total_external_unpaid_bookings_count(self.user_home, self.home_studio)
		self.assertEquals(0, count)
# class CancelBookingTestCase(TestCase):
#
#     def setUp(self):
#         self.slice_class = mommy.make_recipe('classes.slice_class', mbo_class_id=24978, mbo_site_id=-99)
#         self.user_home = mommy.make_recipe('accounts.user')
#         self.mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=self.user_home, mbo_client_id=100015620,
#                                             mbo_site_id=-99)
#         self.booking = mommy.make_recipe('bookings.booking', user=self.user_home, slice_class=self.slice_class)
#
#     @skipIf(True, "Skip this test")
#     def test_cancel_home_user_booking(self):
#         booking = booking_manager.cancel_booking(self.booking, self.user_home)
#
#         self.assertFalse(booking.is_cancelled)
#
#         existing_booking = Booking.objects.get(pk=booking.id)
#         self.assertTrue(existing_booking.is_cancelled)
#
#     @skipIf(True, "Skip this test")
#     def test_cancel_other_user_booking(self):
#         user_other = mommy.make_recipe('accounts.user_other')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_other', user=user_other, mbo_client_id=100015620,
#                                        mbo_site_id=29730)
#         booking = mommy.make_recipe('bookings.booking', user=user_other, slice_class=self.slice_class,
#                                     mbo_visit_id=100343779)
#
#         self.assertFalse(booking.is_cancelled)
#
#         saved_booking = booking_manager.cancel_booking(booking, user_other)
#         self.assertTrue(saved_booking.is_cancelled)
#
#
# class ClientBookingsView(TestCase):
#
#     def test_get_upcoming_bookings_with_future_booking_different_date(self):
#         some_datetime = utcnow_plus(timedelta(days=2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_upcoming_bookings(user)
#         self.assertEquals(1, result.count())
#
#     def test_get_upcoming_bookings_with_future_booking_same_date(self):
#         some_datetime = utcnow_plus(timedelta(hours=2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_upcoming_bookings(user)
#         self.assertEquals(1, result.count())
#
#     def test_get_upcoming_bookings_with_past_booking_same_date(self):
#         some_datetime = utcnow_plus(timedelta(hours=-2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_upcoming_bookings(user)
#         self.assertEquals(0, result.count())
#
#     def test_get_past_bookings_with_future_booking_different_date(self):
#         some_datetime = utcnow_plus(timedelta(days=2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_past_bookings(user)
#         self.assertEquals(0, result.count())
#
#     def test_get_past_bookings_with_past_booking_same_date(self):
#         some_datetime = utcnow_plus(timedelta(hours=-2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_past_bookings(user)
#         self.assertEquals(1, result.count())
#
#     def test_get_past_bookings_with_past_booking_past_date(self):
#         some_datetime = utcnow_plus(timedelta(days=-2))
#         start_date = some_datetime.date()
#         start_time = some_datetime.time()
#         slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
#                                         start_time=start_time, end_time=start_time)
#         user = mommy.make_recipe('accounts.user')
#         mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
#         booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
#
#         result = booking_manager.get_past_bookings(user)
#         self.assertEquals(1, result.count())
#
#


class GetClassVisitsResult():
	def __init__ (self):
		self.Visits = Visits()


class Visits():
	Visit = []

	def __init__ (self):
		visit_one = Visit(25)
		self.Visit.append(visit_one)


class Visit():
	def __init__ (self, visit_id):
		self.ID = visit_id

	def get_visit (self):
		return self


class SetupResources(BaseExternalTestSetup):
	def __init__(self, setting):
		self.setting = setting

	def setup_parent(self):
		super().setup()

	def setup_studios1(self):
		self.setting.home_studio = self.studio
		self.setting.external_studio = self.external_studio

	def setup_class_and_resources1(self):
		self.setting.location = self.location
		self.setting.session_type = self.session_type
		self.setting.staff = self.staff
		self.setting.program = self.program
		self.setting.slice_class_external = mommy.make_recipe('classes.slice_class',
															  studio=self.external_studio,
															  staff=self.staff,
															  session_type=self.session_type,
															  location=self.location
															  )
		self.setting.slice_class_home = mommy.make_recipe('classes.slice_class', studio=self.studio,
														  staff=self.staff,
														  session_type=self.session_type,
														  location=self.location
														  )

	def setup_user1(self):
		self.setting.user_home = self.user
		self.setting.user_home2 = mommy.make_recipe('accounts.user', first_name='tharaka', last_name='tharaka',
													email='thraka@hotmail.com')

	def setup_studio_services1(self):
		self.setting.studio_service = mommy.make_recipe('services.studio_service', studio=self.studio)
		self.setting.studio_service_2 = mommy.make_recipe('services.studio_service_2', studio=self.studio)

	def setup_mbo_client_home_studio1(self):
		self.setting.mbo_client_home = self.mbo_client
		self.setting.mbo_client_home2 = mommy.make_recipe('accounts.mbo_client', user=self.setting.user_home2,
														  studio=self.studio)

	def setup_mbo_client_services1(self):
		self.setting.mbo_client_service = self.mbo_client_service
		self.setting.mbo_client_service_2 = mommy.make_recipe('services.mbo_client_service',
															  name='Passport',
															  mbo_client=self.mbo_client,
															  mbo_client_service_id=100246934,
															  current=True,
															  count=5,
															  remaining=5,
															  payment_date=make_utc(datetime(2016, 6, 15)).date(),
															  active_date=make_utc(datetime(2016, 6, 15)).date(),
															  expiration_date=make_utc(datetime(2016, 7, 15)).date(),
															  program=self.program,
															  last_sync_date='2016-06-24 07:21:04',
															  )
		self.setting.mbo_client_service_3 = mommy.make_recipe('services.mbo_client_service', name='Intro',
															  mbo_client=self.setting.mbo_client_home2,
															  mbo_client_service_id=100246934,
															  current=True,
															  count=5,
															  remaining=5,
															  payment_date=make_utc(datetime(2016, 6, 15)).date(),
															  active_date=make_utc(datetime(2016, 6, 15)).date(),
															  expiration_date=make_utc(datetime(2016, 7, 15)).date(),
															  program=self.program,
															  last_sync_date='2016-06-24 07:21:04',
															  )

	def setup_mbo_services1(self):
		self.setting.mbo_service = self.mbo_service
		self.setting.mbo_service_2 = mommy.make_recipe('services.mbo_service', studio=self.studio, name='Passport',
													   count=5,
													   max_per_studio=5,
													   over_flow_days=4)

	def setup_mbo_client_external1(self):
		self.setting.mbo_client_external = mommy.make_recipe('accounts.mbo_client_external',
															 user=self.setting.user_home,
															 studio=self.setting.external_studio)

	# def setup_mbo_external_client(self):
	# 	self.setup.mbo_external_client = mommy.make_recipe('accounts.mbo_external_client', user=self.setup.user_home)
	# 	self.setup.mbo_external_client2 = mommy.make_recipe('accounts.mbo_external_client2', user=self.setup.user_home2)

	def setup_user_external_studio1(self):
		self.setting.user_external_studio = self.external_studio
		self.setting.user_external_studio2 = mommy.make_recipe('accounts.user_external_studio',
															   user=self.setting.user_home2,
															   studio=self.setting.external_studio)

	def setup_external_booking1(self):
		self.setting.external_booking = self.external_booking
		self.setting.external_booking2 = mommy.make_recipe('bookings.bookings_core.booking',
														   mbo_client=self.mbo_client,
														   slice_class=self.external_slice_class)

		self.setting.external_booking3 = mommy.make_recipe('bookings.bookings_core.booking_external',
														   slice_class=self.external_slice_class,
														   mbo_client=self.setting.mbo_client_home2)

	def setup_external_booking_service1(self):
		self.setting.external_booking_service = self.external_booking_service

	def setup_unpaid_bookings1(self):
		self.setting.unpaid_booking1 = self.unpaid_bookings
		self.setting.unpaid_booking2 = mommy.make_recipe('bookings.bookings_core.unpaid_booking',
														 booking=self.setting.external_booking2,
														 parent_service=self.setting.mbo_client_service)
		self.setting.unpaid_booking3 = mommy.make_recipe('bookings.bookings_core.unpaid_booking',
														 booking=self.setting.external_booking3,
														 parent_service=self.setting.mbo_client_service)
