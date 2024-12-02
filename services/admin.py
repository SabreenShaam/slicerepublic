from django.contrib import admin
from services.models import MboService, MboClientService, PassportStudioAccess


class MboServiceAdmin(admin.ModelAdmin):
    list_display = ('studio', 'name')


class PassportStudioAccessAdmin(admin.ModelAdmin):
    list_select_related = ('mbo_service__studio',)
    list_display = ('get_home_studio', 'mbo_service', 'get_external_studio', 'is_accessible')

    def get_home_studio(self, obj):
        return obj.mbo_service.studio.name

    get_home_studio.short_description = 'Home studio'

    def get_external_studio(self, obj):
        return obj.studio.name

    get_external_studio.short_description = 'External studio'

admin.site.register(MboService, MboServiceAdmin)
admin.site.register(MboClientService)
admin.site.register(PassportStudioAccess, PassportStudioAccessAdmin)
