from model_utils.models import TimeStampedModel
from django.db import models
from venues.models import Studio, Location, MBOLocation, MBOResource
from staff.models import Staff
from django.db.models import Q
from slicerepublic.dateutil import utcnow, get_local_datetime


class ProgramManager(models.Manager):
    def get_program_by_mbo_program_id_and_studio(self, mbo_program_id, studio):
        return self.filter(mbo_program_id=mbo_program_id, site=studio).first()

    def get_integrated_program_id_list_by_studio(self, studio):
        return self.filter(site=studio, is_integrated=True).values_list("mbo_program_id", flat=True)

    def get_integrated_program_id_list_by_mbo_site_id(self, mbo_site_id):
        query = self.filter(site__mbo_site_id=mbo_site_id, is_integrated=True).values_list('mbo_program_id', flat=True)
        return query

    def get_program_by_mbo_program_id_and_studio(self, mbo_program_id, studio_id):
        return self.filter(mbo_program_id=mbo_program_id, site_id=studio_id).first()


class Program(models.Model):
    mbo_program_id = models.PositiveIntegerField()
    site = models.ForeignKey(Studio)
    schedule_type = models.CharField(max_length=50)
    cancel_off_set = models.PositiveIntegerField()
    opens = models.PositiveIntegerField()
    is_integrated = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = ProgramManager()

    def __str__(self):
        return "Studio - {}, Program - {}".format(self.site.name, self.mbo_program_id)


class SessionTypeManager(models.Manager):
    def get_sessiontype_by_mbo_sessiontype_and_site_ids(self, mbo_session_type_id, mbo_site_id):
        return self.filter(mbo_session_type_id=mbo_session_type_id, mbo_site_id=mbo_site_id).first()


class SessionType(models.Model):
    name = models.CharField('Name', max_length=50)
    mbo_session_type_id = models.PositiveIntegerField()
    mbo_site_id = models.IntegerField()
    program_id = models.PositiveIntegerField()
    num_deducted = models.PositiveIntegerField()

    objects = SessionTypeManager()


class ScheduleManager(models.Manager):
    def get_schedule_by_mbo_schedule_id_and_studio(self, mbo_schedule_id, studio_id):
        query = self.filter(mbo_schedule_id=mbo_schedule_id, studio_id=studio_id).first()
        return query


class Schedule(models.Model):
    mbo_schedule_id = models.PositiveIntegerField()
    day_sunday = models.BooleanField(default=False)
    day_monday = models.BooleanField(default=False)
    day_tuesday = models.BooleanField(default=False)
    day_wednesday = models.BooleanField(default=False)
    day_thursday = models.BooleanField(default=False)
    day_friday = models.BooleanField(default=False)
    day_saturday = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    studio = models.ForeignKey(Studio, null=True)

    objects = ScheduleManager()


class SliceClassManager(models.Manager):

    def get_classes_by_date_range_and_studio(self, start_date, end_date, studio_access_list=None):
        qs = self.select_related("mbolocation__location", "session_type", "staff", "studio", "program", "mbo_resource")

        if studio_access_list is not None:
            qs = qs.filter(studio__id__in=studio_access_list)

        qs = qs.filter(
            Q(start_date__gte=start_date),
            Q(end_date__lte=end_date),
            Q(studio__is_active=True),
        )
        return qs

    def get_class_by_mbo_class_id_and_studio(self, mbo_class_id, studio):
        return self.select_related("session_type", "staff", "mbo_resource").\
            filter(mbo_class_id=mbo_class_id, studio=studio).first()

    def get_classes_by_date_and_studio(self, date_of_class=None, studio_access_list=None):
        qs = self.select_related("mbolocation__location", "session_type", "staff", "studio")

        if studio_access_list is not None:
            qs = qs.filter(studio__id__in=studio_access_list)

        qs = qs.filter(
            Q(start_date__gte=date_of_class),
            Q(end_date__lte=date_of_class),
            Q(is_cancelled=False),
            Q(studio__is_active=True),
            Q(is_active=True),
            Q(program__is_active=True),
        ).order_by("start_time")
        return qs

    def get_all_classes_by_date_and_studio(self, date_of_class=None, studio_access_list=None):
        qs = self.select_related("mbolocation__location", "session_type", "staff", "studio")

        if studio_access_list is not None:
            qs = qs.filter(studio__id__in=studio_access_list)

        qs = qs.filter(
            Q(start_date__gte=date_of_class),
            Q(end_date__lte=date_of_class),
            Q(studio__is_active=True),
        ).order_by("start_time")
        return qs

    def get_class_by_id(self, id):
        query = self.filter(id=id).first()
        return query

    def search(self, date_of_class=None):
        qs = self.select_related("mbolocation__location", "session_type", "staff").filter(
            Q(start_date__gte=date_of_class),
            Q(end_date__lte=date_of_class)
        ).order_by("start_time")
        return qs

    def get_classes_by_studio(self, studio_access_list=None):
            qs = self.select_related("staff", "studio")

            if studio_access_list is not None:
                qs = qs.filter(studio__id__in=studio_access_list)

            qs = qs.filter(
                Q(is_cancelled=False),
                Q(studio__is_active=True),
            ).order_by("start_time")
            return qs

    def get_classes_by_studio_ids(self, ids_list):
        qs = self.filter(id__in=ids_list)
        return qs


class SliceClass(TimeStampedModel):
    name = models.CharField('Name', max_length=255)
    mbo_class_id = models.PositiveIntegerField()
    studio = models.ForeignKey(Studio)
    mbo_last_updated = models.DateTimeField()
    description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    staff = models.ForeignKey(Staff)
    session_type = models.ForeignKey(SessionType)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    mbolocation = models.ForeignKey(MBOLocation)
    is_active = models.BooleanField(default=True)
    mbo_resource = models.ForeignKey(MBOResource, blank=True, null=True)
    level = models.CharField('level', max_length=255, null=True)
    schedule = models.ForeignKey(Schedule, blank=True, null=True)
    program = models.ForeignKey(Program, blank=True, null=True)
    objects = SliceClassManager()

    @property
    def bookable(self):
        local_datetime = get_local_datetime(utcnow(), 'Europe/London')

        if self.start_date == local_datetime.date():
            if self.start_time < local_datetime.time():
                return False
        elif self.start_date < local_datetime.date():
            return False
        return True

    # todo : temporary solution, find a permenant solution
    @property
    def location(self):
        return self.mbolocation.location