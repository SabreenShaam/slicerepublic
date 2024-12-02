from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from accounts.models import User
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel
from accounts.models import MboClient
from classes.models import Program
from venues.models import Studio


class MboServiceManager(models.Manager):
    def get_mbo_service_by_name_and_studio(self, name, studio):
        query = self.filter(studio=studio, name=name, is_active=True).first()
        return query

    def get_mbo_services_by_studio(self, studio):
        query = self.filter(studio=studio)
        return query

    def get_service_by_id_and_studio(self, id, studio_id):
        query = self.filter(id=id, studio_id=studio_id).first()
        return query


class MboService(models.Model):
    name = models.CharField(max_length=50)
    studio = models.ForeignKey(Studio)
    count = models.PositiveIntegerField(null=True)
    max_per_studio = models.PositiveIntegerField(null=True)
    over_flow_days = models.PositiveIntegerField(null=True)
    is_active = models.BooleanField(default=True)
    objects = MboServiceManager()

    def change_state(self, is_active):
        self.is_active = is_active
        self.save()

    def __str__(self):
        return self.name


class MboClientServiceManager(models.Manager):
    def get_mbo_client_service_by_mbo_client(self, mbo_client):
        query = self.filter(mbo_client=mbo_client).first()
        return query

    def get_active_services_by_names(self, mbo_client, current_dt, names):
        query = self.filter(Q(expiration_date__gte=current_dt), mbo_client=mbo_client, current=True, name__in=names)
        return query

    def count_active_services_in_names(self, mbo_client, class_date, names):
        query = self.filter(Q(expiration_date__gte=class_date), mbo_client=mbo_client, current=True, name__in=names) \
            .count()
        return query

    def get_active_services_in_names(self, mbo_client, names):
        query = self.filter(Q(mbo_client=mbo_client, name__in=names),
                            Q(current=True) | Q(current=False, remaining=0)).order_by('active_date')
        return query

    def get_service_by_name_and_payment_date(self, mbo_client, name, date):
        query = self.filter(mbo_client=mbo_client, name=name, payment_date=date, current=True).first()
        return query

    def get_active_mbo_client_service(self, mbo_client):
        query = self.filter(mbo_client=mbo_client, current=True).order_by('active_date').first()
        return query

    def get_active_new_mbo_client_service_by_names(self, mbo_client, current_dt, names, remaining_count):
        query = self.filter(Q(expiration_date__gte=current_dt), mbo_client=mbo_client, current=True, name__in=names,
                            remaining=remaining_count).order_by('-created')
        return query

    def get_mbo_client_service_by_id(self, id):
        query = self.raw(
            "SELECT m.id, m.name, m.count, s.online_price, s.tax_rate from services_mboclientservice as m JOIN services_studioservice as s ON(m.name=s.name) WHERE  m.id = %s",
            [id])
        return query


class MboClientService(TimeStampedModel):
    name = models.CharField(max_length=50)
    mbo_client = models.ForeignKey(MboClient)
    mbo_client_service_id = models.PositiveIntegerField()
    current = models.BooleanField()
    count = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()
    payment_date = models.DateField()
    active_date = models.DateField()
    expiration_date = models.DateField()
    program = models.ForeignKey(Program)
    last_sync_date = models.DateTimeField()
    auto_pay = models.BooleanField(default=False)

    objects = MboClientServiceManager()

    def update_auto_pay(self, value):
        self.auto_pay = value
        self.save()

    def as_json(self):
        return dict(
            id=self.id,
            name=self.name,
            online_price=self.online_price,
            tax_rate=self.tax_rate,
            count=self.count)


class StudioServiceManager(models.Manager):
    def get_studio_services_by_studio(self, studio):
        query = self.filter(studio=studio, is_active=True).order_by('online_price', 'name')
        return query

    def get_studio_service_by_id(self, studio_service_id):
        query = self.filter(id=studio_service_id).first()
        return query

    def get_mbo_service_by_name_and_studio(self, name, studio):
        query = self.filter(studio=studio, name=name).first()
        return query


class StudioService(models.Model):
    name = models.CharField(max_length=50)
    mbo_service_id = models.PositiveIntegerField()
    mbo_product_id = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=4)
    online_price = models.DecimalField(max_digits=8, decimal_places=4)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=3)
    count = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    studio = models.ForeignKey(Studio)

    objects = StudioServiceManager()


class ShoppingCart(TimeStampedModel):
    user = models.ForeignKey(User, related_name='ShoppingCart')
    studio_service = models.ForeignKey(StudioService)


class ClientCreditCardInfoManager(models.Manager):
    def get_client_credit_card_info_by_mbo_client(self, mbo_client_id):
        query = self.filter(mbo_client_id=mbo_client_id, is_active=True).first()
        return query


class ClientCreditCardInfo(models.Model):
    mbo_client = models.ForeignKey(MboClient, null=True)
    type = models.CharField(max_length=50)
    last_four = models.PositiveIntegerField()
    exp_month = models.PositiveIntegerField()
    exp_year = models.PositiveIntegerField()
    postal_code = models.CharField(max_length=10, null=True)
    is_active = models.BooleanField(default=True)

    objects = ClientCreditCardInfoManager()


class PassportStudioAccessManager(models.Manager):
    def get_accessible_studios_by_mbo_service(self, mbo_service):
        query = self.select_related('studio').filter(mbo_service=mbo_service, is_accessible=True,
                                                     studio__is_active=True).values('studio')
        return query

    def get_passport_services_by_studio(self, home_studio, class_studio):
        query = self.select_related('mbo_service').filter(mbo_service__studio=home_studio, studio=class_studio,
                                                          is_accessible=True, studio__is_active=True)
        return query

    def get_all_available_studios_by_mbo_service(self, mbo_service_id):
        query = self.raw(
            "SELECT a.id, s.id, s.name, p.drop_in_price, p.ten_pack_price, is_accessible FROM services_passportstudioaccess  a LEFT JOIN venues_studio s ON a.studio_id=s.id LEFT JOIN venues_studiopricing  p  ON s.id=p.studio_id WHERE s.is_active=True AND a.mbo_service_id= %s ORDER BY s.name",
            [mbo_service_id])
        return query


class PassportStudioAccess(models.Model):
    studio = models.ForeignKey(Studio)
    mbo_service = models.ForeignKey(MboService)
    is_accessible = models.BooleanField(default=True)

    objects = PassportStudioAccessManager()

    def update(self, is_accessible):
        self.is_accessible = is_accessible
        self.save()


@receiver(post_save, sender=MboService)
def enable_passport_studio_access_list(sender, **kwargs):
    if kwargs.get('created', False):
        studios = Studio.objects.get_all_active_mbo_studios()
        for studio in studios:
            if kwargs['instance'].studio != studio:
                PassportStudioAccess.objects.create(mbo_service=kwargs['instance'], studio=studio)
