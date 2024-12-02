from django.contrib import admin
from django import forms
from venues.models import Studio, Location, MBOLocation, MBOResource, RoomLocation, StudioSettings, StudioPricing


class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'mbo_site_id')

    def save_model(self, request, obj, form, change):
        obj.save()
        studio_setting = StudioSettings.objects.get_studio_settings_by_studio_id(obj.id)
        if not studio_setting:
            studio_settings = StudioSettings()
            studio_settings.studio = obj
            studio_settings.save()


admin.site.register(Studio, StudioAdmin)
admin.site.register(MBOResource)


class LocationForm(forms.ModelForm):
    class Meta:
        exclude = ('nearest_tube_station',)
        model = Location


class LocationAdmin(admin.ModelAdmin):
    form = LocationForm


admin.site.register(Location, LocationAdmin)
admin.site.register(MBOLocation)
admin.site.register(RoomLocation)


class StudioSettingsAdmin(admin.ModelAdmin):
    list_display = ('studio', 'room_location_enabled')


admin.site.register(StudioSettings, StudioSettingsAdmin)


class StudioPricingAdmin(admin.ModelAdmin):
    list_display = ('studio', 'drop_in_price', 'ten_pack_price')

admin.site.register(StudioPricing, StudioPricingAdmin)