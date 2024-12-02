from django.conf.urls import patterns, include, url
from django.contrib import admin
from home.views import Home
from slicerepublic import settings

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^scheduler/', include('scheduler.urls')),
    url(r'^classes/', include('classes.urls')),
    url(r'^api/bookings/', include('bookings.bookings_api.urls')),
    url(r'^bookings/', include('bookings.bookings_web.urls')),
    url(r'^venues/', include('venues.urls')),
    url(r'^studios/', include('studios.studios_web.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/services/', include('services.urls')),
    url(r'^api/staffs/', include('staff.urls')),
    url(r'^api/fcm/', include('fcm.urls')),
    url(r'^api/ratings/', include('ratings.urls')),
    url(r'^api/notifications/', include('notifications.urls')),
    url(r'^api/customscripts/', include('custom_scripts.urls')),
)

if settings.DEBUG:
    # Serve static files in debug.
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT,
        'show_indexes' : True}),
    )
