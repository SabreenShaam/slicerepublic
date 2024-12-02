from django.contrib import admin
from slice.models import SliceService, SliceClient, SliceServiceProgram


class SliceServiceAdmin(admin.ModelAdmin):
    list_display = ('studio', 'mbo_service_id')


class SliceClientAdmin(admin.ModelAdmin):
    list_display = ('studio', 'mbo_client_id')


class SliceServiceProgramAdmin(admin.ModelAdmin):
    list_display = ('slice_service', 'program')

admin.site.register(SliceService, SliceServiceAdmin)
admin.site.register(SliceClient, SliceClientAdmin)
admin.site.register(SliceServiceProgram, SliceServiceProgramAdmin)
