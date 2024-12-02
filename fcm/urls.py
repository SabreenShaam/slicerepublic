from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from fcm.views import FCMInstanceView

urlpatterns = [
    url(r'^instance$', FCMInstanceView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
