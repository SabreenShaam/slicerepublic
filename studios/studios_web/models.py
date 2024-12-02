from django.db import models
from venues.models import Studio


class StudioAccessManager(models.Manager):
    def create_studio_access(self, home_studio_id, other_studio_id, is_accessible):
        studio_access = self.model(home_studio_id=home_studio_id, other_studio_id=other_studio_id, is_accessible=is_accessible)
        studio_access.save()
        return studio_access

    def get_studio_access_list(self, home_studio):
        query = self.filter(home_studio=home_studio, is_accessible=True).values_list('other_studio_id', flat=True)
        return query

    def get_active_studio_access_list(self):
        query = self.select_related('home_studio', 'other_studio').filter(is_accessible=True)
        return query

    def get_studio_access_item_by_studios(self, home_studio_id, other_studio_id):
        query = self.filter(home_studio_id=home_studio_id, other_studio_id=other_studio_id).first()
        return query

    def get_studio_access_list_for_studio(self, home_studio):
        query = self.select_related('other_studio').filter(home_studio=home_studio)
        return query


class StudioAccess(models.Model):
    home_studio = models.ForeignKey(Studio, related_name='home_studio')
    other_studio = models.ForeignKey(Studio, related_name='other_studio')
    is_accessible = models.BooleanField(default=True)

    class Meta:
        unique_together = (("home_studio", "other_studio"),)

    objects = StudioAccessManager()
