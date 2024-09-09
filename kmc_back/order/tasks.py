from celery import shared_task
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from common.utility import send_email_with_template
from kmc_back import settings
from order.models.order_models import Order
from order.models.refund_models import Refund
from order.utility.order_utility import can_be_paid
from product.models import Product, ProductItem
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
@shared_task
def async_send_order_email(user_id, order_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    order = get_object_or_404(Order, id=order_id)
    context = {
        "email": user.email,
        "name": user.name,
        "code": order.code,
        "created_at": order.created_at,
        "address": order.order_address.address,
        "base_url": settings.BACKEND_URL + "/media/",
        "items": order.order_item.all(),
        "payment_type": order.payment_type,
        "discount": order.discount,
        "shipping_fees": order.shipping_fees,
        "total_price": order.price_paid,
        "Awb_code": order.awb,
    }

    send_email_with_template(
        mail_subject="New KMC refund if",
        template_name="order_email_template.html",
        context=context,
        to_emails=[user.email],
    )
@shared_task
def async_send_refund_email(user_id, order_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    order = get_object_or_404(Order, id=order_id)
    context = {
        "email": user.email,
        "name": user.name,
        "code": order.code,
        "created_at": order.created_at,
        "address": order.order_address.address,
        "base_url": settings.BACKEND_URL + "/media/",
        "items": order.order_item.all(),
        "payment_type": order.payment_type,
        "discount": order.discount,
        "shipping_fees": order.shipping_fees,
        "total_price": order.price_paid,
        "Awb_code": order.awb,
    }

    send_email_with_template(
        mail_subject="New KMC refund else",
        template_name="order_email_template.html",
        context=context,
        to_emails=[user.email],
    )


# @shared_task
# def async_send_refund_email(user_id, refund_id, total):
#     user = get_object_or_404(get_user_model(), id=user_id)
#     refund = Refund.objects.get(id=refund_id)
#     order = refund.order
#     context = {
#         "email": user.email,
#         "name": user.name,
#         "code": order.code,
#         "created_at": order.created_at,
#         "address": order.order_address.address,
#         "base_url": settings.BACKEND_URL + "/media/",
#         "items": order.order_item.filter(order_refund_item__refunded_quantity__gt=0),
#         "payment_type": order.payment_type,
#         "total_price": total,
#     }
#     send_email_with_template(
#         mail_subject="New KMC Refund Created",
#         template_name="refund_email_template.html",
#         context=context,
#         to_emails=[user.email],
#     )


# @shared_task
# def cancel_orders():
#     """Cancel orders after payment duration expires"""

#     orders_to_cancel = Order.objects.prefetch_related("order_item").filter(
#         payment_type="Credit Card", order_status="Awaiting Payment"
#     )

#     for order in orders_to_cancel:
#         if not can_be_paid(order):
#             order.order_status = "Cancelled"
#             order.save(update_fields=["order_status"])
#             # update products items stock again after order cancellation
#             for order_item in order.order_item.all():
#                 try:
#                     product = Product.objects.prefetch_related("product_item").get(
#                         id=order_item.product_uuid
#                     )
#                 except Product.DoesNotExist:
#                     raise Http404("No Product matches the given query.")

#                 if product.product_item:
#                     item = product.product_item.get(id=order_item.product_item_id)
#                     item.stock += order_item.quantity
#                     item.save()
              
#                 else:
#                     product.stock += order_item.quantity
#                     product.save()
                    
@shared_task
def cancel_orders():
    """Cancel orders after payment duration expires"""

    orders_to_cancel = Order.objects.prefetch_related("order_item").filter(
        payment_type="Credit Card", order_status="Awaiting Payment"
    )

    for order in orders_to_cancel:
        if not can_be_paid(order):
            order.order_status = "Cancelled"
            order.save(update_fields=["order_status"])
            
            for order_item in order.order_item.all():
                try:
                    product = Product.objects.prefetch_related("product_item").get(
                        id=order_item.product_uuid
                    )
                except Product.DoesNotExist:
                    raise Http404("No Product matches the given query.")
                
                if order_item.product_item_id:
                    try:
                        item = product.product_item.get(id=order_item.product_item_id)
                        item.stock += order_item.quantity
                        item.save()
                    except ProductItem.DoesNotExist:
                        # Handle the case where the product item ID is invalid or missing
                        logger.warning(f"ProductItem with ID {order_item.product_item_id} does not exist.")
                        continue  # Skip this item and move to the next
                else:
                    product.stock += order_item.quantity
                    product.save()
