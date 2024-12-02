from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from scheduler.views import SyncClasses, SyncLocations, SyncResources, SyncSchedules, SyncUnpaid

urlpatterns = [
    url(r'^sync/classes', SyncClasses.as_view()),
    url(r'^sync/locations', SyncLocations.as_view()),
    url(r'^sync/resources', SyncResources.as_view()),
    url(r'^sync/schedules', SyncSchedules.as_view()),
    url(r'^sync/unpaid', SyncUnpaid.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
