from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class General(models.Model):
    tax_percentage = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], default=0.0)
    point_value = models.FloatField(default=1.0,
                                    validators=[
                                        MinValueValidator(0.0)])  # How much egyptian pound does each point equal to
