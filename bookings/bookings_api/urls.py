from django.conf.urls import url
from bookings.bookings_api.views import BookClass, CancelBooking, UpcomingBooking, PastBooking, ClientSignIn, \
    ExternalCreditsView, ExternalUnpaidBookingView, SyncClientVisitsView, BookingsView

urlpatterns = [
    url(r'^class/(?P<pk>\d+)/book', BookClass.as_view()),
    url(r'^booking/(?P<pk>\d+)/cancel', CancelBooking.as_view()),
    url(r'^upcoming/booking', UpcomingBooking.as_view()),
    url(r'^past/booking', PastBooking.as_view()),
    url(r'^booking/(?P<pk>\d+)/signin', ClientSignIn.as_view()),
    url(r'^external/booking/count', ExternalCreditsView.as_view()),
    url(r'^external/unpaid/booking/count', ExternalUnpaidBookingView.as_view()),
    url(r'^sync/client/visits', SyncClientVisitsView.as_view()),
    url(r'^$', BookingsView.as_view()),
]
