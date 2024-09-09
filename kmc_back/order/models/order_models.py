import hashlib
import os
import uuid
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
from django_resized import ResizedImageField

from coupon.models.coupon_models import Coupon
from product.uitlity.productUtility import (
    allowed_extensions,
    extension_error_message,
    file_size,
)
from user.models.user_address import validate_phone

order_status = [
    ("Ordered", "Ordered"),
    ("Awaiting Payment", "Awaiting Payment"),
    ("Paid", "Paid"),
    # ("Shipped", "Shipped"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
    ("Declined", "Declined"),
    ("Refunded", "Refunded"),
    ("Partially Refunded", "Partially Refunded"),
    ("Refund requested", "Refund requested"),
    ("Transaction Failed", "Transaction Failed"),
]

order_item_status = [
    ("Ordered", "Ordered"),
    # ("Shipped", "Shipped"),
    ("Cancelled", "Cancelled"),
    ("Declined", "Declined"),
    ("Refund Requested", "Refund Requested"),
    ("Refunded", "Refunded"),
]
payment_type = [
    ("Cash On Delivery", "Cash On Delivery"),
    ("Credit Card", "Credit Card"),
]


def get_order_item_image_path(instance, filename):
    return os.path.join("order_item", instance.product_title_en, filename)


def create_verification_code(extra_data=""):
    from datetime import datetime

    now = datetime.now().strftime("YYYY-MM-DD")
    uid = uuid.uuid4()
    code_str = f"{now}-{uid}@{extra_data}"
    return hashlib.sha256(code_str.encode("utf-8")).hexdigest()[0:32]


class Order(models.Model):
    code = models.CharField(unique=True, max_length=12, blank=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="order_user"
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        related_name="order_coupon",
        null=True,
        blank=True,
    )
    price_paid = models.FloatField(validators=[MinValueValidator(1.0)])
    # points_paid = models.PositiveIntegerField(default=0)
    # one_point_value = models.FloatField(default=0.0)  # Value of single point to pound
    # points_value = models.FloatField(validators=[MinValueValidator(0.0)],
    #                                  default=0.0)  # Value of total points in pounds
    total_price = models.FloatField(
        validators=[MinValueValidator(1.0)]
    )  # Total price without any discount (coupon or points)
    discount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=255, choices=order_status)
    shipping_status = models.CharField(max_length=255, default="-")
    payment_type = models.CharField(max_length=255, choices=payment_type)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    registered_order_id = models.CharField(max_length=255, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    tax_value = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    compelted_at = models.DateField(blank=True, null=True)
    order_weight = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    shipping_fees = models.FloatField(default=0.0)
    number_of_boxes = models.FloatField(default=0.0)
    awb = models.CharField(max_length=20, default="")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = create_verification_code(f"#{self.user.id}")[0:8] + str(
                datetime.now().year
            )
        if not self.compelted_at:
            if self.order_status in ["Paid", "Completed", "Shipped"]:
                self.compelted_at = now()
        return super().save(*args, **kwargs)

    def __str__(self):
        # return 'Order Code : ' + self.code + ' - Date : ' + str(self.created_at.date())
        return f"User: {self.user.name} - Order Code: {self.code} - Date: {str(self.created_at.date())} - Register ID: {self.registered_order_id} - Order Status: {self.order_status}"


class OrderAddress(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="order_address"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=11,
        help_text="Maximum length is 11 numbers",
        validators=[validate_phone],
    )
    phone_country_code = models.CharField(max_length=5, default="+20")
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.TextField()
    building = models.CharField(max_length=255, default="")
    floor = models.CharField(max_length=255, blank=True, null=True, default="")
    apartment = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return f"User: {self.name} - Order Code: {self.order.code} - Address: {self.address}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_item"
    )
    product_title_en = models.CharField(max_length=255)
    product_title_ar = models.CharField(max_length=255, null=True)
    product_image = ResizedImageField(
        upload_to=get_order_item_image_path,
        validators=[
            FileExtensionValidator(allowed_extensions, extension_error_message),
            file_size,
        ],
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    # return_points = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=255, choices=order_item_status)
    product_uuid = models.CharField(max_length=255, null=True, blank=True)
    product_item_type = models.CharField(max_length=255, null=True, blank=True)
    product_item_id = models.PositiveIntegerField(null=True, blank=True)
    product_item_title = models.CharField(max_length=255, null=True, blank=True)
    product_item_weight = models.FloatField(
        validators=[MinValueValidator(0.1)], default=0.1
    )

    def __str__(self):
        return f"User: {self.order.user.name} - Order Code: {self.order.code} - Product Title: {self.product_title_en}"

