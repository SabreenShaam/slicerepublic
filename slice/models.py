from django.db import models
from classes.models import Program
from venues.models import Studio


class SliceServiceManager(models.Manager):
    def get_slice_service_by_studio(self, studio):
        query = self.filter(studio=studio).first()
        return query


class SliceService(models.Model):
    studio = models.ForeignKey(Studio)
    mbo_service_id = models.PositiveIntegerField()

    objects = SliceServiceManager()

    def __str__(self):
        return "Studio - {}, MboService  - {}".format(self.studio.name, self.mbo_service_id)


class SliceClient(models.Model):
    studio = models.ForeignKey(Studio)
    mbo_client_id = models.CharField(max_length=100)

    def __str__(self):
        return "Mbo site id - {}".format(self.studio.mbo_site_id)


class SliceServiceProgramManager(models.Manager):
    def get_slice_services_by_program(self, program):
        query = self.select_related('slice_service').filter(program=program)
        return query


class SliceServiceProgram(models.Model):
    slice_service = models.ForeignKey(SliceService)
    program = models.ForeignKey(Program)

    objects = SliceServiceProgramManager()
