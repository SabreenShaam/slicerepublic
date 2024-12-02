from django.conf.urls import patterns, url
from bookings.bookings_web.views import BookingView


urlpatterns = patterns(
    '',
    url(r'^$', BookingView.as_view(), name='bookings'),
)