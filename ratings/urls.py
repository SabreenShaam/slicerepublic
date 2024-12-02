from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ratings.views import RatingsView

urlpatterns = [
    url(r'^(?P<pk>\d+)/class$', RatingsView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
