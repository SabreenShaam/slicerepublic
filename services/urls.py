from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from services.views import ClientServiceView, CheckoutServiceView, StudioServiceListView, ServiceSummaryView, \
    ClientCreditCardInfoView, StoredCardCheckoutView, MboServiceUpdateView, MboServiceSummaryView, \
    StudioPortalServicesView, UpdateAutoPayOption, ClientServiceInfoView, PassportStudioAccessView

urlpatterns = [
    url(r'^client/service$', ClientServiceView.as_view()),
    url(r'^studio/service$', StudioServiceListView.as_view()),
    url(r'^(?P<pk>\d+)/service/buy$', CheckoutServiceView.as_view()),
    url(r'^(?P<pk>\d+)/service/buy/summary$', ServiceSummaryView.as_view()),
    url(r'^client/service/storedcard$', ClientCreditCardInfoView.as_view()),
    url(r'^(?P<pk>\d+)/service/buy/storedcard$', StoredCardCheckoutView.as_view()),
    url(r'^service/update$', MboServiceUpdateView.as_view()),
    url(r'^service/summary$', MboServiceSummaryView.as_view()),
    url(r'^studio/service/portal$', StudioPortalServicesView.as_view()),
    url(r'^(?P<pk>\d+)/service/autopay/(?P<state>.*)$', UpdateAutoPayOption.as_view()),
    url(r'^(?P<pk>\d+)/service/', ClientServiceInfoView.as_view()),
    url(r'^service/(?P<pk>\d+)/studio-access$', PassportStudioAccessView.as_view()),



]

urlpatterns = format_suffix_patterns(urlpatterns)
