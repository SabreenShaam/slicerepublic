from datetime import timedelta
from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from classes.models import SliceClass
from accounts.models import User, MboClient
from django.db.models import Q
from services.models import StudioService, MboService, MboClientService
from slicerepublic import dateutil


class BookingManager(models.Manager):
    def get_class_bookings(self, mbo_class_id, studio):
        return self.filter(Q(slice_class__mbo_class_id=mbo_class_id) & Q(slice_class__studio=studio)) \
            .values_list('mbo_visit_id', flat=True)

    def get_upcoming_classes(self, mbo_client_id, current_date, current_time):
        return self.select_related('slice_class__studio', 'slice_class__mbolocation__location', 'slice_class__staff',
                                   'slice_class__studio'). \
            filter((Q(slice_class__start_date__gt=current_date) | (Q(slice_class__start_date=current_date) &
                                                                   Q(slice_class__start_time__gte=current_time))),
                   mbo_client_id=mbo_client_id, is_cancelled=False, late_cancelled=False,
                   sync_status=Booking.SYNCHED_STATUS, slice_class__studio__is_active=True) \
            .order_by('slice_class__start_date', 'slice_class__start_time')

    def get_past_classes(self, mbo_client_id, current_date, current_time):
        return self.select_related('slice_class__studio', 'slice_class__mbolocation__location', 'slice_class__staff',
                                   'slice_class__studio'). \
            filter((Q(slice_class__start_date__lt=current_date) | (Q(slice_class__start_date=current_date) &
                                                                   Q(slice_class__start_time__lte=current_time))),
                   mbo_client_id=mbo_client_id, is_cancelled=False, sync_status=Booking.SYNCHED_STATUS,
                   slice_class__studio__is_active=True) \
            .order_by('slice_class__start_date', 'slice_class__start_time')

    def search_bookings(self, studio=None, from_date=None, to_date=None):
        qs = self.filter(slice_class__start_date__gte=from_date, slice_class__start_date__lte=to_date)

        if studio:
            qs = qs.filter(slice_class__studio=studio)
        return qs

    def get_bookings_by_mbo_client_site_and_date_range(self, mbo_client_id, studio, start_date, end_date):
        return self.filter((Q(slice_class__start_date__gte=start_date)
                            & (Q(slice_class__start_date__lte=end_date)
                               & Q(slice_class__studio=studio))),
                           mbo_client_id=mbo_client_id)

    def get_all_booking_by_mbo_client_and_date(self, mbo_client_id, start_date):
        return self.filter(Q(slice_class__start_date=start_date), mbo_client_id=mbo_client_id, is_cancelled=False,
                           late_cancelled=False, sync_status=Booking.SYNCHED_STATUS). \
            select_related('slice_class', 'slice_class__mbolocation__location')

    def get_booking_by_mbo_client_and_class(self, mbo_client_id, slice_class_id):
        query = self.select_related('slice_class', 'slice_class__mbolocation__location'). \
            filter(mbo_client_id=mbo_client_id, slice_class_id=slice_class_id, is_cancelled=False, late_cancelled=False,
                   sync_status=Booking.SYNCHED_STATUS).first()
        return query

    def get_external_bookings_count_by_service(self, mbo_client_id, mbo_client_service_id):
        query = self.select_related('slice_class', 'slice_class__studio'). \
            filter(mbo_client_id=mbo_client_id,
                   is_cancelled=False,
                   externalbookingservice__mbo_client_service_id=mbo_client_service_id).count()
        return query

    def get_external_bookings_count(self, mbo_client_id, home_studio_id, from_date, to_date):
        query = self.select_related('slice_class', 'slice_class__studio'). \
            filter(created__range=(from_date, to_date),
                   mbo_client_id=mbo_client_id,
                   is_cancelled=False). \
            exclude(slice_class__studio_id=home_studio_id).count()
        return query

    def get_external_bookings_count_by_studio(self, mbo_client_id, class_studio_id, mbo_client_service_id):
        query = self.select_related('slice_class', 'slice_class__studio'). \
            filter(mbo_client_id=mbo_client_id,
                   is_cancelled=False,
                   externalbookingservice__mbo_client_service_id=mbo_client_service_id,
                   slice_class__studio_id=class_studio_id).count()
        return query

    def create_booking(self, mbo_client, slice_class, mbo_visit_id, is_mbo_booking, sync_status, **extra_fields):
        booking = self.model(mbo_client=mbo_client,
                             slice_class=slice_class,
                             mbo_visit_id=mbo_visit_id,
                             is_mbo_booking=is_mbo_booking,
                             sync_status=sync_status, **extra_fields)
        booking.save()
        return booking

    def get_bookings_users_by_class(self, class_id):
        query = self.select_related('mbo_client__user', 'slice_class').filter(slice_class__id=class_id)
        return query

    def search(self, page, **kwargs):
        query = self.__get_search_query(**kwargs).order_by('-slice_class__start_date')
        if page:
            start = (page - 1) * settings.SEARCH_PAGE_LIMIT
            end = start + settings.SEARCH_PAGE_LIMIT
            query = query[start:end]
        else:
            query = query[:settings.SEARCH_PAGE_LIMIT]

        return query

    def count(self, **kwargs):
        query = self.__get_search_query(**kwargs)
        return query.count()

    def __get_search_query(self, **kwargs):
        filters = {
            'user_email': 'mbo_client__user__email__icontains',
            'first_name': 'mbo_client__user__first_name__icontains',
            'last_name': 'mbo_client__user__last_name__icontains',
            'home_studio': 'mbo_client__studio__name__icontains',
            'class_studio': 'slice_class__studio__name__icontains',
            'is_cancelled': 'is_cancelled',
            'late_cancelled': 'late_cancelled',
            'sync_status': 'sync_status',
            'signed_in': 'signed_in',
        }

        exclude_filters = {
            'ex_home_studio': 'mbo_client__studio__name__icontains',
            'ex_class_studio': 'slice_class__studio__name__icontains',
        }

        arguments = {}
        exclude_arguments = {}
        for key, value in kwargs.items():
            if key != 'start_date' and key != 'end_date':
                if key in exclude_filters:
                    exclude_arguments[exclude_filters[key]] = value
                elif key in filters:
                    arguments[filters[key]] = value

                    # for key, value in kwargs.items():
                    #     if key not in filters:
                    #         exclude_arguments[exclude_filters[key]] = value

        if 'start_date' not in kwargs:
            start_date = dateutil.utc_today_midnight_plus(timedelta(days=-365))
        else:
            start_date = dateutil.datetime.strptime(kwargs['start_date'], '%Y-%m-%d')

        if 'end_date' not in kwargs:
            end_date = dateutil.utc_today_midnight_plus(timedelta(days=1))
        else:
            end_date = dateutil.datetime.strptime(kwargs['end_date'], '%Y-%m-%d')

        arguments['slice_class__start_date__range'] = [start_date, end_date]

        arguments['is_mbo_booking'] = False
        query = self.select_related('mbo_client', 'slice_class', 'slice_class__studio').filter(**arguments).exclude(
            **exclude_arguments)
        return query

    def get_signed_in_class_users_by_date(self, class_date, from_time, to_time):
        query = self.select_related('slice_class', 'mbo_client').filter(Q(slice_class__start_date=class_date) & Q(slice_class__end_time__gte=from_time) & Q(slice_class__end_time__lte=to_time)).values('mbo_client_id', 'slice_class__id', 'slice_class__name')
        return query

    def get_booking_by_id(self, booking_id):
        query = self.select_related('slice_class').filter(id=booking_id).first()
        return query

    def get_user_bookings_by_user_first_name(self, name, date_range):
        query = self.select_related('slice_class__studio').filter(is_cancelled=False, mbo_client__user__first_name__icontains=name, created__range=date_range)
        return query


class Booking(TimeStampedModel):
    UNKNOWN_STATUS = 1
    SYNCHED_STATUS = 2

    SYNC_STATUS_CHOICES = (
        (UNKNOWN_STATUS, 'Unknown'),
        (SYNCHED_STATUS, 'Synched'),
    )

    # todo : remove user field
    user = models.ForeignKey(User, related_name='bookings', null=True)
    mbo_client = models.ForeignKey(MboClient, null=True)
    slice_class = models.ForeignKey(SliceClass, related_name='bookings')
    mbo_visit_id = models.PositiveIntegerField(null=True)
    is_cancelled = models.BooleanField(default=False)
    late_cancelled = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    signed_in = models.BooleanField(default=False)
    is_mbo_booking = models.BooleanField(default=True)
    sync_status = models.IntegerField(choices=SYNC_STATUS_CHOICES, default=UNKNOWN_STATUS)

    objects = BookingManager()

    def cancel(self):
        self.is_cancelled = True
        self.save()

    @staticmethod
    def get_results(bookings):
        results = []
        for booking in bookings:
            booking_item = {}
            booking_item['email'] = booking.mbo_client.user.email
            booking_item['first_name'] = booking.mbo_client.user.first_name
            booking_item['last_name'] = booking.mbo_client.user.last_name
            booking_item['class_name'] = booking.slice_class.name
            booking_item['class_studio'] = booking.slice_class.studio.name
            booking_item['home_studio'] = booking.mbo_client.studio.name
            booking_item['booking_date'] = booking.created.date()
            booking_item['class_start_date'] = booking.slice_class.start_date
            booking_item['class_start_time'] = booking.slice_class.start_time
            booking_item['cancelled'] = booking.is_cancelled
            booking_item['late_cancelled'] = booking.late_cancelled
            booking_item['sync_status'] = booking.sync_status
            booking_item['signed_in'] = booking.signed_in
            results.append(booking_item)
        return results


class ExternalBookingServiceManager(models.Manager):
    def create_external_booking(self, booking, mbo_client_service):
        booking_service = self.model(booking=booking, mbo_client_service=mbo_client_service)
        booking_service.save()
        return booking_service

    def get_external_booking_count_by_mbo_client_and_passport(self, mbo_client, from_date, to_date, passport_service):
        query = self.select_related('mbo_client_service', 'booking').filter(
            booking__created__range=(from_date, to_date), booking__mbo_client=mbo_client,
            service__name=passport_service.name).count()
        return query


class ExternalBookingService(models.Model):
    booking = models.ForeignKey(Booking)
    mbo_client_service = models.ForeignKey(MboClientService, null=True)

    objects = ExternalBookingServiceManager()


class UnpaidBookingsManager(models.Manager):
    def create_unpaid_bookings(self, booking, parent_service):
        unpaid_booking = self.model(booking=booking, parent_service=parent_service)

        unpaid_booking.save()
        return unpaid_booking

    def get_active_unpaid_bookings(self):
        query = self.select_related('booking', 'parent_service', 'booking__slice_class__studio',
                                    'booking__mbo_client').filter(booking__is_cancelled=False, is_paid=False)
        return query

    def get_external_unpaid_bookings_count_by_studio(self, mbo_client_id, class_studio_id, mbo_client_service_id):
        query = self.select_related('booking__slice_class', 'booking__slice_class__studio', 'booking'). \
            filter(booking__mbo_client_id=mbo_client_id,
                   booking__slice_class__studio_id=class_studio_id,
                   booking__is_cancelled=False,
                   is_paid=False,
                   parent_service_id=mbo_client_service_id).count()
        return query

    def get_external_bookings_for_unpaid_booking(self, mbo_client_id, mbo_client_service_name):
        query = self.select_related('booking__slice_class', 'booking__slice_class__studio', 'booking'). \
            filter(booking__mbo_client_id=mbo_client_id, booking__is_cancelled=False, is_paid=False,
                   parent_service__name=mbo_client_service_name)
        return query

    def get_external_bookings_count_for_unpaid_booking(self, mbo_client_id, home_studio_id, parent_service):
        query = self.select_related('booking__slice_class', 'booking__slice_class__studio', 'booking'). \
            filter(booking__mbo_client_id=mbo_client_id, is_paid=False, booking__is_cancelled=False,
                   parent_service=parent_service).count()
        return query

    def get_total_external_unpaid_bookings_count(self, mbo_client_id):
        query = self.select_related('booking__slice_class', 'booking__slice_class__studio', 'booking'). \
            filter(booking__mbo_client_id=mbo_client_id, is_paid=False, booking__is_cancelled=False).count()
        return query

    def make_booking_as_paid(self, booking):
        booking.is_paid = True
        booking.save()


class UnpaidBookings(TimeStampedModel):
    booking = models.ForeignKey(Booking)
    is_paid = models.BooleanField(default=False)
    parent_service = models.ForeignKey(MboClientService, null=True)

    objects = UnpaidBookingsManager()

    def mark_as_paid(self):
        self.is_paid = True
        self.save()
