from bookings.bookings_core.models import Booking, UnpaidBookings
from django.conf import settings


class Credits(object):
	@staticmethod
	def get_used_external_credits (mbo_client, from_date, to_date):
		used_external_credits = Booking.objects.get_external_bookings_count_for_service(mbo_client.id,
																			mbo_client.studio.id,
																			from_date,
																			to_date)
		return used_external_credits

	@staticmethod
	def get_used_external_credits_by_service(mbo_client, mbo_service_client_id):
		used_external_credits = Booking.objects.get_external_bookings_count_by_service(mbo_client.id,
																					   mbo_service_client_id)
		return used_external_credits

	@staticmethod
	def get_external_bookings_count_for_unpaid_booking(mbo_client, mbo_client_service):
		used_external_credits = UnpaidBookings.objects.get_external_bookings_count_for_unpaid_booking(mbo_client.id, mbo_client.studio.id, mbo_client_service)
		return used_external_credits

	@staticmethod
	def get_used_external_credits_by_studio(mbo_client, mbo_client_service_id, class_studio_id):
		used_external_credits = Booking.objects.get_external_bookings_count_by_studio(mbo_client.id,
																					  class_studio_id,
																					  mbo_client_service_id)
		return used_external_credits

	@staticmethod
	def get_external_unpaid_bookings_count_by_studio(mbo_client, mbo_client_service_id, class_studio_id):
		used_external_credits = UnpaidBookings.objects.get_external_unpaid_bookings_count_by_studio(mbo_client.id,
																									class_studio_id,
																									mbo_client_service_id)
		return used_external_credits

	@staticmethod
	def get_total_external_unpaid_bookings_count(mbo_client):
		unpaid_bookings = UnpaidBookings.objects.get_total_external_unpaid_bookings_count(mbo_client.id)
		return unpaid_bookings

	@staticmethod
	def get_total_external_credits ():
		return settings.EXTERNAL_CREDIT_LIMIT
