from model_mommy import mommy
from model_mommy.recipe import Recipe
from accounts.models import UserExternalStudio
from bookings.bookings_core.models import ExternalBookingService


class BaseTestSetup(object):
	def __init__(self):
		self.studio = None
		self.location = None
		self.session_type = None
		self.staff = None
		self.program = None
		self.user = None
		self.studio_service = None
		self.mbo_client = None
		self.mbo_client_service = None
		self.mbo_service = None
		self.client_credit_card_info = None

	def setup(self):
		self.setup_studio()
		self.setup_location()
		self.setup_session_type()
		self.setup_staff()
		self.setup_base_program()
		self.setup_user()
		self.setup_studio_service()
		self.setup_mbo_client()
		self.setup_mbo_client_service()
		self.setup_mbo_services()
		self.setup_client_credit_card_info()

	def setup_studio(self):
		self.studio = mommy.make_recipe('venues.studio', name='Slice Urban Fitness', mbo_site_id=29730)

	def setup_location(self):
		self.location = mommy.make_recipe('venues.location')

	def setup_session_type(self):
		self.session_type = mommy.make_recipe('classes.session_type')

	def setup_staff(self):
		self.staff = mommy.make_recipe('staff.staff')

	def setup_base_program(self):
		self.program = mommy.make_recipe('classes.program', site=self.studio)

	def setup_user(self):
		self.user = mommy.make_recipe('accounts.user')

	def setup_studio_service(self):
		self.studio_service = mommy.make_recipe('services.studio_service', studio=self.studio)

	def setup_mbo_client(self):
		self.mbo_client = mommy.make_recipe('accounts.mbo_client',
											user=self.user,
											studio=self.studio)

	def setup_mbo_client_service(self):
		self.mbo_client_service = mommy.make_recipe('services.mbo_client_service',
													mbo_client=self.mbo_client,
													program=self.program
													)

	def setup_mbo_services(self):
		self.mbo_service = mommy.make_recipe('services.mbo_service', studio=self.studio)

		# def setup_unpaid_bookings(self):
		#     self.unpaid_booking = Recipe(
		#         UnpaidBookings,
		#         booking=self.external_booking,
		#         parent_service=self.mbo_client_service
		#     ).make()

	def setup_client_credit_card_info(self):
		self.client_credit_card_info = mommy.make_recipe('services.client_credit_card_info',
													mbo_client=self.mbo_client)


class BaseExternalTestSetup(BaseTestSetup):
	def __init__(self):
		self.external_studio = None
		self.program = None
		self.external_slice_class = None
		self.user_external_studio = None
		self.external_booking = None
		self.external_booking_service = None
		self.mbo_client_external = None
		self.mbo_external_client = None
		self.unpaid_bookings = None

	def setup(self):
		super().setup()
		#self.setup_studio()
		self.setup_program()
		self.setup_class()
		self.setup_user_external_studio()
		self.setup_booking()
		self.setup_external_booking_service()
		self.setup_mbo_client_external()
		self.setup_mbo_external_client()
		self.setup_unpaid_bookings()

	def setup_studio(self):
		super().setup_studio()
		self.external_studio = mommy.make_recipe('venues.studio', name='Slice Live', mbo_site_id=22612)

	def setup_program(self):
		self.program = mommy.make_recipe('classes.program', site=self.external_studio)

	def setup_class(self):
		self.external_slice_class = mommy.make_recipe('classes.slice_class',
													  studio=self.external_studio,
													  staff=self.staff,
													  session_type=self.session_type,
													  location=self.location
													  )

	def setup_user_external_studio(self):
		self.user_external_studio = Recipe(
			UserExternalStudio,
			user=self.user,
			studio=self.external_studio
		).make()

	def setup_booking(self):
		self.external_booking = mommy.make_recipe('bookings.bookings_core.booking',
												  mbo_client=self.mbo_client,
												  slice_class=self.external_slice_class)

	def setup_external_booking_service(self):
		self.external_booking_service = Recipe(
			ExternalBookingService,
			booking=self.external_booking,
			mbo_client_service=self.mbo_client_service
		).make()

	def setup_mbo_client_external(self):
		self.mbo_client_external = mommy.make_recipe('accounts.mbo_client_external', user=self.user,
														   studio=self.external_studio)

	def setup_mbo_external_client(self):
		self.mbo_external_client = mommy.make_recipe('accounts.mbo_external_client', user=self.user)

	def setup_unpaid_bookings(self):
		self.unpaid_bookings = mommy.make_recipe('bookings.bookings_core.unpaid_booking',
													  booking=self.external_booking,
													  parent_service=self.mbo_client_service)
