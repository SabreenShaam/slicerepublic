from django.contrib import admin
from studios.studios_web.models import StudioAccess


class StudioAccessAdmin(admin.ModelAdmin):
    list_display = ('home_studio', 'other_studio')

admin.site.register(StudioAccess, StudioAccessAdmin)
