from django.db import models
from .tfl_manager import get_nearest_rail_station
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from model_utils.models import TimeStampedModel
from venues.venues_util import calculate_drop_in_transfer_price, calculate_ten_pack_transfer_price, \
    calculate_transfer_price


class StudioManager(models.Manager):
    def get_studio_by_mbo_site_id(self, mbo_site_id):
        return self.filter(mbo_site_id=mbo_site_id).first()

    def get_studio_by_studio_id(self, studio_id):
        return self.get(pk=studio_id)

    def get_all_mbo_studios(self):
        query = self.filter(is_mbo_studio=True)
        return query

    def get_all_active_mbo_studios(self):
        query = self.filter(is_mbo_studio=True, is_active=True).order_by('name')
        return query

    def get_external_studio_access_list(self, home_studio_id):
        query = self.raw(
            "select other.id, other.name, access.is_accessible from venues_studio as home CROSS JOIN venues_studio as other LEFT JOIN studios_web_studioaccess as access on (home.id = access.home_studio_id AND other.id = access.other_studio_id)  where home.id = %s and (home.id != other.id)",
            [home_studio_id])

        return query


class Studio(models.Model):
    name = models.CharField('Name', max_length=255)
    mbo_site_id = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    contact_email = models.EmailField(max_length=255, null=True)
    is_mbo_studio = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    site_url = models.TextField(null=True)
    image = models.ImageField(upload_to='images/studio/', default='images/studio/default.png')
    logo = models.ImageField(upload_to='images/studio/', default='images/studio/default_logo.png')
    objects = StudioManager()

    def __str__(self):
        return self.name

    def deactivate(self):
        self.is_active = False
        self.save()


class Location(models.Model):
    name = models.CharField('Name', max_length=255)
    business_description = models.TextField()
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    postcode = models.CharField(max_length=10, null=True)
    phone = models.CharField(max_length=14)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    description = models.TextField()
    nearest_rail_station = models.ForeignKey('RailStation', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        data = get_nearest_rail_station(self.latitude, self.longitude)
        if data is not None:
            tfl_stoppoint_id = data['stopPoints'][0]['id']
            rail_station = RailStation.objects.get_rail_station_by_tfl_stoppoint_id(tfl_stoppoint_id)
            if rail_station:
                self.nearest_rail_station = rail_station
            else:
                rail_station = RailStation()
                common_name = data['stopPoints'][0]['commonName']
                rail_station.name = common_name.replace('Underground Station', '').rstrip()
                rail_station.name = rail_station.name.replace('Rail Station', '').rstrip()
                rail_station.latitude = data['stopPoints'][0]['lat']
                rail_station.longitude = data['stopPoints'][0]['lon']
                for additional_property in data['stopPoints'][0]['additionalProperties']:
                    if additional_property['key'] == 'Address':
                        address = additional_property['value'].rsplit(',', 1)
                        rail_station.postcode = address[1]
                        break
                rail_station.tfl_stoppoint_id = tfl_stoppoint_id
                rail_station.save()

                self.nearest_rail_station = rail_station
        super(Location, self).save(*args, **kwargs)


class MBOLocationManager(models.Manager):
    def get_mbolocation_by_studio_id_and_mbo_location_id(self, studio_id, mbo_location_id):
        return self.filter(studio_id=studio_id, mbo_location_id=mbo_location_id).first()

    def get_mbolocations_by_studio_id(self, studio_id):
        return self.select_related('location').filter(studio_id=studio_id)

    def get_mbolocation_count_by_studio_id(self, studio_id):
        query = self.filter(studio_id=studio_id).count()
        return query


class MBOLocation(models.Model):
    location = models.ForeignKey(Location)
    mbo_location_id = models.PositiveIntegerField()
    studio = models.ForeignKey(Studio, related_name='locations')

    objects = MBOLocationManager()

    def __str__(self):
        return "{} - {}".format(self.studio.name, self.location.name)


class MBOResourceManager(models.Manager):
    def get_mboresource_by_studio_id_and_mbo_resource_id(self, studio_id, mbo_resource_id):
        return self.filter(studio_id=studio_id, mbo_resource_id=mbo_resource_id).first()


class MBOResource(models.Model):
    name = models.CharField(max_length=50)
    studio = models.ForeignKey(Studio)
    mbo_resource_id = models.PositiveIntegerField()

    objects = MBOResourceManager()

    def __str__(self):
        return "{} - {}".format(self.studio.name, self.name)


class RoomLocationManager(models.Manager):
    def get_room_location_by_mbo_resource_id(self, mbo_resource_id):
        query = self.select_related('studio', 'location').filter(room_id=mbo_resource_id).first()
        return query


class RoomLocation(models.Model):
    location = models.ForeignKey(Location)
    room = models.ForeignKey(MBOResource)
    studio = models.ForeignKey(Studio)

    objects = RoomLocationManager()

    def __str__(self):
        return "{} - {}".format(self.studio.name, self.room.name)


class StudioSettingsManager(models.Manager):
    def get_studio_settings_by_studio_id(self, studio_id):
        query = self.filter(studio_id=studio_id).first()
        return query


class StudioSettings(models.Model):
    studio = models.ForeignKey(Studio)
    room_location_enabled = models.BooleanField(default=False)

    objects = StudioSettingsManager()


class RailStationManager(models.Manager):
    def get_rail_station_by_tfl_stoppoint_id(self, tfl_stoppoint_id):
        query = self.filter(tfl_stoppoint_id=tfl_stoppoint_id).first()
        return query


class RailStation(models.Model):
    name = models.CharField(max_length=60)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    postcode = models.CharField(max_length=10, null=True)
    tfl_stoppoint_id = models.CharField(max_length=40)

    objects = RailStationManager()

    def __str__(self):
        return self.name


class StudioPricingManager(models.Manager):
    def get_studio_pricing_by_id(self, studio_id):
        query = self.select_related('studio').filter(studio_id=studio_id, is_active=True).first()
        return query

    def get_all_studio_pricing(self):
        query = self.select_related('studio').filter(is_active=True, studio__is_active=True)
        return query

    def get_studio_pricing_by_studio_id(self, id):
        query = self.filter(studio_id=id, is_active=True, studio__is_active=True).first()
        return query


class StudioPricing(TimeStampedModel):
    studio = models.ForeignKey(Studio, null=True)
    drop_in_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    ten_pack_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True)

    objects = StudioPricingManager()

    def deactivate(self):
        self.is_active = False
        self.save()

    @property
    def drop_in_transfer_price(self):
        drop_in = calculate_drop_in_transfer_price(self.drop_in_price)
        return drop_in

    @property
    def ten_pack_transfer_price(self):
        ten_pack = calculate_ten_pack_transfer_price(self.ten_pack_price)
        return ten_pack

    @property
    def transfer_price(self):
        return calculate_transfer_price(self.drop_in_price, self.ten_pack_price)


@receiver(post_save, sender=Studio)
def enable_studio_access_list(sender, **kwargs):
    if kwargs.get('created', False):
        from studios.studios_web.models import StudioAccess
        studios = Studio.objects.get_all_active_mbo_studios()
        for studio in studios:
            if kwargs['instance'] != studio:
                StudioAccess.objects.create(home_studio=kwargs['instance'], other_studio=studio)
                StudioAccess.objects.create(home_studio=studio, other_studio=kwargs['instance'])
