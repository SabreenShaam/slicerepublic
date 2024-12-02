from django.test import TestCase
from unittest.mock import patch
from unittest import skipIf
from model_mommy import mommy
from rest_framework import status
from datetime import timedelta
from slicerepublic.dateutil import utcnow_plus
import json


@skipIf(True, "Skip this test")
class BookingsViewTestCase(TestCase):
	def setUp(self):
		self.slice_class = mommy.make_recipe('classes.slice_class')
		self.user = mommy.make_recipe('accounts.user')

		self.mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=self.user)
		self.mbo_client_service = mommy.make_recipe('services.mbo_client_service', mbo_client=self.mbo_client)

		self.token = mommy.make_recipe('accounts.token', user=self.user)
	# self.booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=self.slice_class)

	@skipIf(True, "Skip this test")
	@patch('bookings.views.book_class')
	def test_book_post(self, mock_book_class):
		slice_class = mommy.make_recipe('classes.slice_class')
		self.booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=slice_class)

		mock_book_class.return_value = self.booking

		auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
		response = self.client.post('/bookings/api/book/1/class', **auth_header)
		self.assertEquals(status.HTTP_201_CREATED, response.status_code)

	# @skipIf(True, "Skip this test")
	# @patch('bookings.views.book_class')
	# def test_book_post(self, mock_book_class):
	#     slice_class = mommy.make_recipe('classes.slice_class')
	#     self.booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=slice_class)

	#
	#     # Mock book_class method in booking_manager
	#     mock_book_class.return_value = self.booking
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
	#     response = self.client.post('/bookings/api/book/1/class', **auth_header)
	#     self.assertEquals(status.HTTP_201_CREATED, response.status_code)
	#
	# @skipIf(True, "Skip this test")
	# @patch('bookings.views.cancel_booking')
	# def test_cancel_booking_unauthenticated_user(self, mock_cancel_booking):
	#
	#     # Mock cancel_booking method in booking_manager
	#     mock_cancel_booking.return_value = True
	#
	#     response = self.client.post('/bookings/api/1/cancel')
	#     self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)
	#
	#     self.assertEquals(0, mock_cancel_booking.call_count)
	#
	# @skipIf(True, "Skip this test")
	# @patch('bookings.views.cancel_booking')
	# def test_cancel_booking(self, mock_cancel_booking):
	#     slice_class = mommy.make_recipe('classes.slice_class')
	#     booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=slice_class)
	#
	#     # Mock cancel_booking method in booking_manager
	#     mock_cancel_booking.return_value = True
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
	#     response = self.client.post('/bookings/api/1/cancel', **auth_header)
	#     self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
	#
	#     self.assertEquals(1, mock_cancel_booking.call_count)
	#
	# @skipIf(True, "Skip this test")
	# @patch('bookings.views.cancel_booking')
	# def test_cancel_booking_with_invalid_booking_id(self, mock_cancel_booking):
	#     slice_class = mommy.make_recipe('classes.slice_class')
	#     booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=slice_class)
	#
	#     # Mock cancel_booking method in booking_manager
	#     mock_cancel_booking.return_value = True
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
	#     response = self.client.post('/bookings/api/2/cancel', **auth_header)
	#     self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
	#
	#     content = json.loads(response.content.decode('utf-8'))
	#     self.assertEquals(20000, content['code'])
	#
	#     self.assertEquals(0, mock_cancel_booking.call_count)
	#
	# @skipIf(True, "Skip this test")
	# def test_upcoming_client_booking_unauthorized_user(self):
	#     response = self.client.get('/bookings/api/upcoming/1/client/booking')
	#     self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)
	#
	# @skipIf(True, "Skip this test")
	# @patch('bookings.views.get_upcoming_bookings')
	# def test_upcoming_client_booking(self, mock_upcoming_bookings):
	#
	#     # Mock upcoming bookings method in booking_manager
	#     mock_upcoming_bookings.return_value = True
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
	#     response = self.client.get('/bookings/api/upcoming/booking', **auth_header)
	#     self.assertEquals(status.HTTP_200_OK, response.status_code)
	#
	#     self.assertEquals(1, mock_upcoming_bookings.call_count)
	#
	# @skipIf(False, "Skip this test")
	# def test_upcoming_client_booking_with_result(self):
	#     some_datetime = utcnow_plus(timedelta(hours=2))
	#     start_date = some_datetime.date()
	#     start_time = some_datetime.time()
	#
	#     slice_class = mommy.make_recipe('classes.slice_class', start_date=start_date, end_date=start_date,
	#                                     start_time=start_time, end_time=start_time)
	#     user = mommy.make_recipe('accounts.user', email='vinusha88@gmail.com')
	#     mbo_client = mommy.make_recipe('accounts.mbo_client_home', user=user)
	#     booking = mommy.make_recipe('bookings.booking', user=user, slice_class=slice_class)
	#     token = mommy.make_recipe('accounts.token', user=user, key="b8fc2a7ffdc098")
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + token.key}
	#     response = self.client.get('/bookings/api/upcoming/booking'.format(user.id), **auth_header)
	#     self.assertEquals(status.HTTP_200_OK, response.status_code)
	#
	#     content = json.loads(response.content.decode('utf-8'))
	#     self.assertEquals(1, len(content))
	#
	#     self.assertTrue(isinstance(content[0]['slice_class'], dict))
	#
	#
	# @skipIf(False, "Skip this test")
	# def test_upcoming_client_booking_with_empty_result(self):
	#     slice_class = mommy.make_recipe('classes.slice_class')
	#     booking = mommy.make_recipe('bookings.booking', user=self.user, slice_class=slice_class)
	#
	#     auth_header = {'HTTP_AUTHORIZATION': 'Token ' + self.token.key}
	#     response = self.client.get('/bookings/api/upcoming/booking'.format(self.user.id), **auth_header)
	#     self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
