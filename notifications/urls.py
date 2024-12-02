from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from notifications.views import NotificationView

urlpatterns = [
    url(r'^$', NotificationView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
