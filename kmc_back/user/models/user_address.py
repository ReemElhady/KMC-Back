# from django.core import validators
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from smsa.models import ZoneCity


def validate_phone(phone):
    if not phone[0:2] == "01":
        raise ValidationError("phone number is not valid.")


class UserAddress(models.Model):
    user = models.ForeignKey(
        get_user_model(), related_name="userAddress", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=11,
        help_text="Maximum length is 11 numbers",
        validators=[validate_phone],
    )
    phone_country_code = models.CharField(max_length=5, default="+20")
    country = models.CharField(max_length=255)
    city = models.ForeignKey(
        ZoneCity,
        on_delete=models.CASCADE,
        related_name="zone_city_addresses",
    )
    address = models.TextField()
    building = models.CharField(max_length=255)
    floor = models.CharField(max_length=255, blank=True, null=True)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name
