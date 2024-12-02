from datetime import timedelta
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.authentication import CustomTokenAuthentication
from accounts.models import MboClient

from classes.models import SliceClass, Program
from bookings.bookings_core.models import Booking

from bookings.bookings_core.booking_manager import book_class, cancel_booking, get_upcoming_bookings, get_past_bookings, \
    sign_in, \
    populate_external_booking_credits_details, get_total_external_unpaid_bookings_count, sync_client_visits

from classes.exceptions import SliceClassDoesNotExistException
from bookings.bookings_core.exceptions import OutsideOfBookingWindowException, BookingDoesNotExistException
from slicerepublic import dateutil
from slicerepublic.exceptions import InvalidParameterException

from bookings.bookings_core import booking_manager
from bookings.bookings_api.serializers import BookingSerializer
from slicerepublic.dateutil import utcnow_plus


class BookClass(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        self.logger.info("Entered BookClass view (class id : {})".format(pk))
        try:
            slice_class = SliceClass.objects.select_related('studio', 'program').get(pk=pk)
        except SliceClass.DoesNotExist:
            message = "Slice Class not found for the ID/Invalid ID : {}".format(pk)
            self.logger.error(message)
            raise SliceClassDoesNotExistException("60000", "Invalid SliceClass id", message)

        if not self.can_book(slice_class):
            message = 'This class is out of booking window.'
            self.logger.error(message)
            raise OutsideOfBookingWindowException("70010", "Booking failed", message)

        booking = book_class(slice_class, request.user, request.auth.studio)

        serializer = BookingSerializer(booking)
        self.logger.info("Leaving BookClass view")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def can_book(self, slice_class):
        close_date = utcnow_plus(timedelta(days=slice_class.program.opens)).date()
        start_date = slice_class.start_date
        if start_date <= close_date:
            return True
        return False


class CancelBooking(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        try:
            booking = Booking.objects.select_related("slice_class__studio", "slice_class__program").get(pk=pk)
        except Booking.DoesNotExist:
            message = "Booking id is invalid"
            self.logger.error(message)
            raise BookingDoesNotExistException("70000", "Invalid Parameter", message)

        late_cancel = self.get_late_cancel()
        if late_cancel:
            if late_cancel != 'true' and late_cancel != 'false':
                message = "late_cancel: Invalid Parameter"
                self.logger.error(message)
                raise InvalidParameterException("10200", "Invalid Parameter", message)
        cancel_booking(booking, request.user, request.auth.studio, late_cancel)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_late_cancel(self):
        return self.request.GET.get('late_cancel')


class UpcomingBooking(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered UpcomingBooking view [user : {}]".format(request.user.email))
        bookings = get_upcoming_bookings(request.user, request.auth.studio)
        # todo : this count requires a db call. Can eliminate the db call
        if bookings.count() == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        lat, lng = self.get_latitude_and_longitude()
        upcoming_bookings = booking_manager.get_upcoming_booking_response(bookings, lat, lng)
        self.logger.info("Leaving UpcomingBooking view [user : {}]".format(request.user.email))
        return Response(upcoming_bookings, status=status.HTTP_200_OK)

    def get_latitude_and_longitude(self):
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        return lat, lng


class PastBooking(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.info("Entered PastBooking view [user : {}]".format(request.user.email))
        bookings = get_past_bookings(request.user, request.auth.studio)
        # todo : this count requires a db call. Can eliminate the db call
        if bookings.count() == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        past_bookings = booking_manager.get_past_bookings_response(bookings)
        self.logger.info("Leaving PastBooking view [user : {}]".format(request.user.email))
        return Response(past_bookings, status=status.HTTP_200_OK)


class ExternalCreditsView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.debug("Entered ExternalCreditsView [user : {}]".format(request.user.email))
        item_details = populate_external_booking_credits_details(request.user, request.auth.studio)
        self.logger.debug("Leaving ExternalCreditsView [user : {}]".format(request.user.email))
        return Response(item_details, status=status.HTTP_200_OK)


class ClientSignIn(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        self.logger.info("Entered ClientSignIn view [user : {}, booking id : {})".format(request.user.email, pk))

        try:
            booking = Booking.objects.select_related("slice_class__studio").get(pk=pk)
        except Booking.DoesNotExist:
            message = "Booking id is invalid"
            self.logger.error(message)
            raise BookingDoesNotExistException("70000", "Invalid Parameter", message)

        sign_in(booking)
        response = booking_manager.get_sign_in_response(booking)
        self.logger.info("Leaving ClientSignIn view [user : {}, booking id : {})".format(request.user.email, pk))
        return Response(response, status=status.HTTP_200_OK)


class ExternalUnpaidBookingView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        self.logger.debug("Entered ExternalUnpaidBookingView [user : {}]".format(request.user.email))
        response = get_total_external_unpaid_bookings_count(request.user, request.auth.studio)
        if response:
            return Response([response], status=status.HTTP_200_OK)
        self.logger.debug("Leaving ExternalUnpaidBookingView [user : {}]".format(request.user.email))

        return Response(status=status.HTTP_204_NO_CONTENT)


class SyncClientVisitsView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        self.logger.debug("Entered SyncClientVisitsView")
        mbo_clients = MboClient.objects.all()
        start_dt = dateutil.get_local_datetime(dateutil.utcnow_plus(timedelta(days=-45)), "Europe/London")
        end_dt = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")
        for mbo_client in mbo_clients:
            try:
                sync_client_visits(mbo_client, start_dt.date(), end_dt.date())
            except:
                self.logger.error("Not Synced for mbo_client id {}".format(mbo_client.id))

        self.logger.debug("Leaving SyncClientVisitsView")
        return Response(status=status.HTTP_200_OK)


class BookingsView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, format=None):
        self.logger.info("Entering BookingsView")

        page = self.get_page()
        search_filters = self.get_search_filters()
        count = Booking.objects.count(**search_filters)
        bookings = Booking.objects.search(page, **search_filters)
        results = Booking.get_results(bookings)

        response = {}
        response['count'] = count
        response['bookings'] = results

        self.logger.info("Leaving BookingsList")
        return Response(response, status=status.HTTP_200_OK)

    def get_page(self):
        page = self.request.query_params.get('page')
        if page:
            return int(page)

    def get_search_filters(self):
        query_param_keys = [
            'start_date',
            'end_date',
            'user_email',
            'first_name',
            'last_name',
            'home_studio',
            'class_studio',
            'class_start_date',
            'is_cancelled',
            'late_cancelled',
            'sync_status',
            'signed_in',
            'ex_home_studio',
            'ex_class_studio',
        ]

        kwargs = {}
        for key in query_param_keys:
            if self.request.query_params.get(key):
                kwargs[key] = self.request.query_params.get(key)

        return kwargs
