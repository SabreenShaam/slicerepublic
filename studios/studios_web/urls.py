from django.conf.urls import patterns, url
from studios.studios_web.views import StudioStaffSignUpView, SignUpVerificationView, StudioStaffLoginView, StudioHome, ViewBookings

urlpatterns = patterns(
    '',
    url(r'^$', StudioHome.as_view(), name="studio_home"),
    url(r'^signup/$', StudioStaffSignUpView.as_view(), name="studio_staff_signup"),
    url(r'^verify', SignUpVerificationView.as_view(), name="studio_signup_verify"),
    url(r'^login', StudioStaffLoginView.as_view(), name="studio_staff_login"),
    url(r'^logout', 'django.contrib.auth.views.logout', kwargs={'next_page': '/studios'}, name="studio_staff_logout"),
    url(r'^bookings', ViewBookings.as_view(), name='studio_bookings')
)