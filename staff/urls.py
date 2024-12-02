from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from staff.views import StaffValidationView

urlpatterns = [
    url(r'^staff/auth$', StaffValidationView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
