from django.contrib import admin
from django.db.models import F, Sum, FloatField
from django.shortcuts import get_object_or_404
from django.utils.html import format_html

from kmc_back.settings import FRONT_URL
from order.models.order_models import OrderItem
from order.models.refund_models import Refund, RefundItem
from order.payment.payment import kashier_refund
from order.tasks import async_send_refund_email
from product.models import Product
from smsa.smsa import SMSAIntegration


class RefundItemInline(admin.TabularInline):
    model = RefundItem
    extra = 0
    # readonly_fields = (
    #     "order_item",
    #     "requested_quantity",
    #     "reason",
    #     "order_item_link",
    #     "refunded_quantity"
    # )

    # help_texts = {'reason': "Unique identifier for the Item", }

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def order_item_link(self, obj):
        from django.utils.safestring import mark_safe

        product = get_object_or_404(Product, id=obj.order_item.product_uuid)
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                # reverse("admin:order_orderitem_change", args=(obj.order_item.pk,)),
                f"{FRONT_URL}products/details/{product.type.id}/{obj.order_item.product_uuid}",
                obj.order_item.product_title_en,
            )
        )


class RefundAdmin(admin.ModelAdmin):
    inlines = [RefundItemInline]
    readonly_fields = ("reason", "order")

    def response_change(self, request, obj):
        obj = self.after_saving_model_and_related_inlines(obj)
        return super(RefundAdmin, self).response_change(request, obj)

    def after_saving_model_and_related_inlines(self, obj):
        order_data = obj.refund_item.filter(to_refund_quantity__gte=1).aggregate(
            total=Sum(
                F("order_item__price") * F("to_refund_quantity"),
                output_field=FloatField(),
            ),
        )
        refunded_items = obj.refund_item.filter(to_refund_quantity__gte=1)
        coupon_percentage = (
            obj.order.coupon.discount_percentage if obj.order.coupon else 0.0
        )
        # points_percentage = (obj.order.points_value / obj.order.total_price) * 100
        total = order_data.get("total")
        total -= (coupon_percentage / 100) * order_data.get("total")
        if obj.order.payment_type == "Credit Card":
            refund_response = kashier_refund(
                transaction_id=obj.order.transaction_id,
                order_id=obj.order.registered_order_id,
                amount=total,
            )
        else:
            refund_response = True

        # Create SMSA Return shipment
        response = SMSAIntegration.return_shipment(refunded_items)
        errors = ""
        if response.json().get("errors"):
            errors += "Error in creating smsa return shipment"

        if refund_response is True:

            OrderItem.objects.filter(order_refund_item__refund=obj).update(
                status="Refunded"
            )

            order_all_items = OrderItem.objects.filter(order=obj.order)
            if (
                order_all_items.count()
                == order_all_items.filter(status="Refunded").count()
            ):
                obj.order.order_status = "Refunded"
            else:
                obj.order.order_status = "Partially Refunded"
            obj.order.save()
            for item in obj.refund_item.all():
                Product.objects.filter(id=item.order_item.product_uuid).update(
                    stock=F("stock") + item.to_refund_quantity
                )
            obj.refund_item.all().update(
                refunded_quantity=F("refunded_quantity") + F("to_refund_quantity"),
                to_refund_quantity=0,
            )

            async_send_refund_email.delay(
                user_id=obj.order.user.id, refund_id=obj.id, total=total
            )
        else:
            obj.refund_item.all().update(to_refund_quantity=0)
            errors += " ** " + refund_response
        if errors:
            return format_html(f'<span style="color: red">{errors}</span>')

        return obj


admin.site.register(Refund, RefundAdmin)
