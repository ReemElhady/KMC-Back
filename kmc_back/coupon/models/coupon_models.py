from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from django.db import models
from product.models import Product

class Coupon(models.Model):
    code = models.CharField(max_length=8, unique=True, validators=[MinLengthValidator(6)])
    discount_percentage = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    expire_date = models.DateField()
    users = models.ManyToManyField(get_user_model(), blank=True)
    usages_per_user = models.PositiveIntegerField(default=0)
    max_discount_value = models.PositiveIntegerField(default=0)
    min_value_to_apply = models.PositiveIntegerField(default=0)
    is_home = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True)  
    
    def save(self, *args, **kwargs):
        self.code = self.code.lower()
        if self.is_home:
            Coupon.objects.filter(is_home=True).exclude(id=self.id).update(
                is_home=False)
        else:
            is_home_coupons = Coupon.objects.filter(is_home=True).exclude(id=self.id).count()
            if not is_home_coupons:
                self.is_home = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
