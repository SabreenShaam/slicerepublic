from rest_framework.views import APIView
from rest_framework.response import Response
from scheduler import sync_classes, sync_venues, sync_schedules
from bookings.bookings_core.booking_manager import handle_unpaid_bookings

from datetime import datetime, timedelta
from slicerepublic import dateutil


class SyncClasses(APIView):

    def get(self, request, format=None):
        # start = dateutil.utcnow_plus(timedelta(days=-4))
        start = dateutil.utcnow()
        print(start)
        # end = dateutil.utcnow_plus(timedelta(days=14))
        mbo_site_ids = 29730
        end = dateutil.utcnow_plus(timedelta(days=14))
        sync_classes.sync_classes(start, end, mbo_site_ids)
        return Response({'Success': 'True'})


class SyncLocations(APIView):

    def get(self, request, format=None):
        mbo_site_ids = 29730
        sync_venues.sync_locations(mbo_site_ids)
        return Response({'Success': 'True'})


class SyncResources(APIView):
    def get(self, request, format=None):
        mbo_site_ids = 29730
        sync_venues.sync_resources(mbo_site_ids)
        return Response({'Success': 'True'})


class SyncSchedules(APIView):
    def get(self, request, format=None):
        mbo_site_ids = 29730
        sync_schedules.sync_schedules(mbo_site_ids)
        return Response({'Success': 'True'})


class SyncUnpaid(APIView):
    def get(self, request, format=None):
        handle_unpaid_bookings()
        return Response({'Success': 'True'})

