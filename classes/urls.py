from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from classes.views import ClassListView, ClassView, StudioClassListView, ClassCancellationView, ClassVisitsView

urlpatterns = [
    url(r'^api/class/$', ClassListView.as_view()),
    url(r'^api/class/(?P<pk>\d+)/$', ClassView.as_view()),
    url(r'^api/class/(?P<pk>\d+)/cancel$', ClassCancellationView.as_view()),
    url(r'^api/class/(?P<pk>\d+)/studio/$', StudioClassListView.as_view()),
    url(r'^api/class/(?P<pk>\d+)/visits/$', ClassVisitsView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
