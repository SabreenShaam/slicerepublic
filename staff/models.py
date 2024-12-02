from django.db import models


class Staff(models.Model):
    mbo_site_id = models.IntegerField()
    mbo_staff_id = models.BigIntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    is_male = models.BooleanField(default=True)
    image_url = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    mobile_phone = models.CharField(max_length=12, null=True)

    class Meta:
        unique_together = (('mbo_site_id', 'mbo_staff_id'),)

    def update(self):
        self.save()
