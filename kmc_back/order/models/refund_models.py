from django.core.exceptions import ValidationError
from django.db import models
from django_extensions.db.models import TimeStampedModel

from order.models.order_models import Order, OrderItem


class Refund(TimeStampedModel):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="refund_order"
    )
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order Code :  {self.order.code} - Date : {str(self.created.date())}"


class RefundItem(models.Model):
    refund = models.ForeignKey(
        Refund, on_delete=models.CASCADE, related_name="refund_item"
    )
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="order_refund_item"
    )
    requested_quantity = models.PositiveIntegerField()
    refunded_quantity = models.PositiveIntegerField(default=0)
    reason = models.TextField(null=True, blank=True)
    to_refund_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order Code : {self.refund.order.code} - {self.order_item.product_title_en} - {str(self.requested_quantity)}"

    class Meta:
        unique_together = (("refund", "order_item"),)

    def clean(self):
        if self.to_refund_quantity + self.refunded_quantity > self.requested_quantity:
            raise ValidationError(
                "To refund quantity and refunded quantity must be lower than or equal requested quantity"
            )

    def save(self, *args, **kwargs):
        if self.to_refund_quantity + self.refunded_quantity <= self.requested_quantity:
            self.refunded_quantity += self.to_refund_quantity
        super().save(*args, **kwargs)
