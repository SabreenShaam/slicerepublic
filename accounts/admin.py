from django.contrib import admin
from accounts.models import AppVersion


class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('platform', 'version')

# Register your models here.
admin.site.register(AppVersion, AppVersionAdmin)
