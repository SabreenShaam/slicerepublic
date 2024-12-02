from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from venues.views import StudioList, StudioInfoView, GetStudioAccessListView, UpdateStudioAccessListView, \
    StudioPricingView, StudioPricingInfoView

urlpatterns = [
    url(r'^api/studio/$', StudioList.as_view()),
    url(r'^api/studio/(?P<pk>\d+)/$', StudioInfoView.as_view()),
    url(r'^api/studio/(?P<pk>\d+)/access-list$', GetStudioAccessListView.as_view()),
    url(r'^api/studio/(?P<studio_id>\d+)/access/(?P<ext_studio_id>\d+)', UpdateStudioAccessListView.as_view()),
    url(r'^api/studio/price', StudioPricingView.as_view()),
    url(r'^api/studio/(?P<pk>\d+)/price', StudioPricingInfoView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
