from bookings.bookings_api.credits import Credits
from bookings.bookings_api.utils import is_paid_booking

import logging


class OverFlowRule(object):
	logger = logging.getLogger(__name__)

	def __init__(self, mbo_client_services, mbo_client_service, mbo_service, class_date):
		self.next_rule = None
		self.mbo_client_services = mbo_client_services
		self.mbo_client_service = mbo_client_service
		self.mbo_service = mbo_service
		self.class_date = class_date

	def set_next_rule(self, next_rule):
		self.next_rule = next_rule

	def check(self):
		if is_paid_booking(self.mbo_client_service, self.class_date):
			self.next_rule.check()
		else:
			delta = self.__get_overflow_days()
			if not delta.days <= self.mbo_service.over_flow_days:
				# remove from the list
				self.mbo_client_services.remove(self.mbo_client_service)
			self.next_rule.check()
		return

	def __get_overflow_days(self):
		overflow_days = self.class_date - self.mbo_client_service.expiration_date
		return overflow_days


class ExternalCountRule(object):
	logger = logging.getLogger(__name__)

	def __init__(self, mbo_client_services, mbo_client, mbo_client_service, mbo_service, class_date):
		self.next_rule = None
		self.mbo_client_services = mbo_client_services
		self.mbo_client = mbo_client
		self.mbo_client_service = mbo_client_service
		self.mbo_service = mbo_service
		self.class_date = class_date

	def set_next_rule(self, next_rule):
		self.next_rule = next_rule

	def check(self):
		if is_paid_booking(self.mbo_client_service, self.class_date):
			is_pass = self.external_credits_count_check_for_paid_booking()
			if is_pass:
				self.next_rule.check()
			else:
				self.mbo_client_services.remove(self.mbo_client_service)
		else:
			is_pass = self.external_credits_count_check_for_unpaid_booking()
			if is_pass:
				self.next_rule.check()
			else:
				self.mbo_client_services.remove(self.mbo_client_service)

		return

	def external_credits_count_check_for_paid_booking(self):
		used_external_credits = Credits.get_used_external_credits_by_service(self.mbo_client, self.mbo_client_service.id)
		return self.validate(used_external_credits)

	def external_credits_count_check_for_unpaid_booking(self):
		used_external_credits = Credits.get_external_bookings_count_for_unpaid_booking(self.mbo_client, self.mbo_client_service)
		return self.validate(used_external_credits)

	def validate(self, used_external_credits):
		is_count_remaining = True
		if used_external_credits >= self.mbo_service.count:
			is_count_remaining = False

		return is_count_remaining


class MaximumPerStudioRule(object):
	logger = logging.getLogger(__name__)

	def __init__(self, mbo_client_services, mbo_client, mbo_client_service, mbo_service, class_date, class_studio):
		self.next_rule = None
		self.mbo_client_services = mbo_client_services
		self.mbo_client = mbo_client
		self.mbo_client_service = mbo_client_service
		self.mbo_service = mbo_service
		self.class_date = class_date
		self.class_studio = class_studio

	def check(self):
		if is_paid_booking(self.mbo_client_service, self.class_date):
			is_pass = self.get_used_external_credits_by_studio_for_paid_booking(self.mbo_client_service)
			if not is_pass:
				self.mbo_client_services.remove(self.mbo_client_service)
		else:
			is_pass = self.get_used_external_credits_by_studio_for_unpaid_booking(self.mbo_client_service)
			if not is_pass:
				self.mbo_client_services.remove(self.mbo_client_service)

		return

	def get_used_external_credits_by_studio_for_paid_booking(self, mbo_client_service):
		used_external_credits = Credits.get_used_external_credits_by_studio(self.mbo_client, mbo_client_service.id, self.class_studio.id)
		return self.validate(used_external_credits)

	def get_used_external_credits_by_studio_for_unpaid_booking(self, mbo_client_service):
		used_external_credits = Credits.get_external_unpaid_bookings_count_by_studio(self.mbo_client, mbo_client_service.id, self.class_studio.id)
		return self.validate(used_external_credits)

	def validate(self, used_external_credits):
		is_max_per_studio_remaining = True
		if used_external_credits >= self.mbo_service.max_per_studio:
			is_max_per_studio_remaining = False

		return is_max_per_studio_remaining
