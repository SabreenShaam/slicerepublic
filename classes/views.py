from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from classes.f_class_visits import FClassVisits

from classes.models import SliceClass
from classes.class_manager import get_class_item, get_class_items, get_class_list_by_studio, \
    cancel_a_class_and_send_email_to_clients, get_class_status
from slicerepublic import dateutil

from slicerepublic.dateutil import utcnow, make_utc

from datetime import datetime
from accounts.authentication import CustomTokenAuthentication

from django.conf import settings
import logging


class ClassListView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)

    def get(self, request, format=None):
        user = request.user
        studio = request.auth.studio
        date_of_class = self.get_date_of_class()
        lat, lng = self.get_latitude_and_longitude()
        page = self.get_page()
        page_count = self.get_page_count()

        class_item_list = get_class_items(user, studio, date_of_class, page, page_count, lat, lng)

        return Response(class_item_list, status=status.HTTP_200_OK)

    def get_date_of_class(self,):
        date_of_class = self.request.GET.get('date')
        if not date_of_class:
            date_of_class = utcnow().date()
        else:
            selected_date = make_utc(datetime.strptime(date_of_class, '%d/%m/%Y'))
            date_of_class = selected_date.date()

        return date_of_class

    def get_latitude_and_longitude(self):
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        return lat, lng

    def get_page(self):
        page = self.request.query_params.get('page', None)
        if page is not None:
            page = int(page)
        return page

    def get_page_count(self):
        page_count = self.request.query_params.get('pageCount', settings.DEFAULT_PAGE_COUNT)
        return int(page_count)


class ClassView(APIView):
    logger = logging.getLogger(__name__)
    authentication_classes = (CustomTokenAuthentication,)

    def get(self, request, pk, format=None):
        slice_class = SliceClass.objects.get_class_by_id(pk)

        if not slice_class:
            return Response(status.HTTP_404_NOT_FOUND)

        lat, lng = self.get_latitude_and_longitude()

        if request.auth:
            class_item = get_class_item(slice_class=slice_class, user=request.user, home_studio=request.auth.studio, lat=lat, lng=lng)
        else:
            class_item = get_class_item(slice_class=slice_class, user=request.user, home_studio=None, lat=lat, lng=lng)

        return Response(class_item, status=status.HTTP_200_OK)

    def get_latitude_and_longitude(self):
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        return lat, lng


class StudioClassListView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk, format=None):
        self.logger.info("Entered StudioClassList View.")
        if request.DATA:
            date = self.request.DATA['search_date']
        else:
            date = dateutil.get_local_datetime(dateutil.utcnow(), "Europe/London")

        class_item_list = get_class_list_by_studio(date, pk)
        self.logger.info("Leaving StudioClassList View.")
        return Response(class_item_list, status=status.HTTP_200_OK)


class ClassCancellationView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk, format=None):
        self.logger.info("Entered ClassCancellationView")
        is_cancelled = get_class_status(pk)
        if is_cancelled:
            cancel_a_class_and_send_email_to_clients(pk)
            response = {'code': 100010}
            self.logger.debug("Class was cancelled in MBO")
        else:
            response = {'code': 100020}
            self.logger.debug("Class was not cancelled in MBO")

        self.logger.info("Leaving ClassCancellationView")
        return Response(response, status=status.HTTP_200_OK)


class ClassVisitsView(APIView):
    logger = logging.getLogger(__name__)

    def get(self, request, pk, format=None):
        self.logger.info("Entered ClassVisitsView.")
        f_slice_class = FClassVisits(pk)
        response = f_slice_class.get_class_visits()
        self.logger.info("Leaving ClassVisitsView.")
        return Response(response, status=status.HTTP_200_OK)
