from django.views.generic import ListView
from bookings.bookings_core.models import Booking
from slicerepublic.dateutil import utcnow, make_utc
from datetime import datetime
from venues.models import Studio
from accounts.models import Staff


class BookingView(ListView):
    model = Booking
    template_name = "bookings/bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        mbo_site_id = self.get_mbo_site_id()
        from_date = self.get_from_date()
        to_date = self.get_to_date()

        if not self.request.user.is_anonymous() and not self.request.user.is_superuser:
            user_id = self.request.user.id
            staff = Staff.objects.get_staff_by_user_id(user_id)
            studio = staff.studio

        qs = Booking.objects.search_bookings(studio, from_date, to_date)
        return qs

    def get_context_data(self, **kwargs):
        context = super(BookingView, self).get_context_data(**kwargs)
        studios = Studio.objects.all()
        context['studios'] = studios

        studio_map = {}

        for studio in studios:
            studio_map[studio.mbo_site_id] = studio.name

        context['studio_map'] = studio_map

        if self.request.GET.get('location'):
            context['location'] = int(self.request.GET.get('location'))

        if self.request.GET.get('from_date'):
            context['from_date'] = self.request.GET.get('from_date')

        if self.request.GET.get('to_date'):
            context['to_date'] = self.request.GET.get('to_date')

        return context

    def get_mbo_site_id(self):
        location = self.request.GET.get('location')
        mbo_site_id = None
        if location and location != '0':
            studio = Studio.objects.get(pk=location)
            mbo_site_id = studio.mbo_site_id
        return mbo_site_id

    def get_from_date(self):
        from_date = self.request.GET.get('from_date')
        if not from_date:
            from_date = utcnow().date()
        else:
            selected_date = make_utc(datetime.strptime(from_date, '%d/%m/%Y'))
            from_date = selected_date.date()
        return from_date

    def get_to_date(self):
        to_date = self.request.GET.get('to_date')
        if not to_date:
            to_date = utcnow().date()
        else:
            selected_date = make_utc(datetime.strptime(to_date, '%d/%m/%Y'))
            to_date = selected_date.date()
        return to_date