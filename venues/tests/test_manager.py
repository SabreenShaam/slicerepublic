from datetime import datetime
from unittest import skipIf

from django.test import TestCase
from model_mommy import mommy

from slicerepublic.base_test_setup import BaseExternalTestSetup
from slicerepublic.dateutil import make_utc
from studios.studios_web.models import StudioAccess
from venues.venue_manager import StudioAccessList


@skipIf(False, "Skip this test")
class VenuesTestCase(TestCase):
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
		setup_resources.setup_studio_access()

	@skipIf(True, "Skip this test")
	def test_studio_access_list(self):
		studio_access_list = StudioAccessList()
		studio_access_list._populate_access_list(1)
		list_items = studio_access_list.get_studio_access_list()
		self.assertEquals(list_items[0]['name'], 'Slice Live')

	@skipIf(False, "Skip this test")
	def test_update_or_create_studio_access(self):
		studio_access_list = StudioAccessList()
		studio_access_list.update_or_create_studio_access(1, 2, 'False')
		studio_access_objs = StudioAccess.objects.all()

		self.assertEquals(studio_access_objs[0].is_accessible, False)




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

	def setup_studio_access(self):
		self.setting.studio_access = mommy.make_recipe('venues.studio_access',
													   home_studio=self.setting.home_studio,
													   other_studio=self.setting.external_studio,
													   is_accessible=False)