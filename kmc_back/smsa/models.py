from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Zone(models.Model):
    name = models.CharField(max_length=100, default="Zone Name")
    first_1_kg_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_1_kg_price = models.DecimalField(max_digits=10, decimal_places=2)
    cod_up_to_cod_limit = models.DecimalField(max_digits=10, decimal_places=2)
    cod_above_cod_limit = models.DecimalField(
        decimal_places=2,
        max_digits=3,
        default=0.1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ],
    )
    cod_limit = models.FloatField(default=3000.0)

    def __str__(self):
        return self.name


class ZoneCity(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100, default="City Name", unique=True)

    def __str__(self):
        return self.name

# shipping fees 
class ShippingFees(models.Model):
    fuel_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=12.00)
    postal_agency_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=14.00)
    government_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        verbose_name = "Shipping Fee"
        verbose_name_plural = "Shipping Fees"

    def __str__(self):
        return "Shipping Fees"
