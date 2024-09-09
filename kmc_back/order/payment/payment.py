import datetime
import hashlib
import hmac
import json

import requests
from django.http import Http404
from django.shortcuts import get_object_or_404
from order.models.order_models import Order
from order.tasks import async_send_order_email
from product.models import Product, ProductItem
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
now = datetime.datetime.now()

# common config
KASHIER_PAYMENT_URL = "https://checkout.kashier.io/"
KASHIER_REFUND_URL = "https://test-api.kashier.io/"
CURRENCY = "EGP"
# live config
MARCHANT_ID = "MID-8830-987"
KASHIER_API_KEY = "bafca527-d7a6-4019-94ea-36e0417b8016"
KASHIER_SECRET_KEY = "b537190657e9f8e8faae7c86c3dac233$84f1d59cd94db5be84790030d76854a57aa1b24fdb6e0a2ff855072e44b6e03086ab83db055f2b437421266f7dd67b69"
KASHIER_REDIRECT_URL = "https://www.kandilmedical.com/api/order/payment-callback/"

# testing config
# MARCHANT_ID ="MID-27572-218"
# KASHIER_SECRET_KEY ="abac191b174300b905452d4144ac8c66$2445d918f5f6a1fbc3b76dfbe3946e5c1562c88113186536b7fbddd06c133c0b581ab3d916824fae057ee4e16058b871"
# KASHIER_API_KEY = "105a8d17-340b-4253-833d-d73ca0aef9bf"
# KASHIER_REDIRECT_URL = "http://127.0.0.1:2271/api/order/payment-callback/"



def return_list_of_order_items(order):
    items_list = []
    order_items = order.order_item.all()
    for item in order_items:
        items_list.append(
            {
                "name": f"{item.product_title_en} ",
                "amount_cents": f"{item.price * 100}",
                "description": " ",
                "quantity": f"{item.quantity}",
            },
        )
    return items_list


def kashier_hash(order):
    mid = MARCHANT_ID  # your merchant id
    amount = order.price_paid  # eg: 100
    currency = CURRENCY  # eg: "EGP"
    orderId = order.id  # eg: 99, your system order ID
    path = "/?payment={}.{}.{}.{}".format(mid, orderId, amount, currency)
    path = bytes(path, "utf-8")
    secret = KASHIER_API_KEY
    secret = bytes(secret, "utf-8")
    return hmac.new(secret, path, hashlib.sha256).hexdigest()


def kashier_generate_iframe(order):
    hash = kashier_hash(order)
    mode = "live"
    # mode = "test"

    type_ = "external"
    language = "en"
    return f"{KASHIER_PAYMENT_URL}?merchantId={MARCHANT_ID}&orderId={order.id}&amount={order.price_paid}&currency={CURRENCY}&hash={hash}&mode={mode}&merchantRedirect={KASHIER_REDIRECT_URL}&display={language}&type={type_}"


def kashier_base_callback(order_id, is_success, transaction_id, registered_order_id):
    
    order = get_object_or_404(Order, id=order_id)
    if is_success in ["true", True, "True"]:
        order.order_status = "Paid"
        order.shipping_status = "Preparing for Delivery"
        order.transaction_id = transaction_id
        order.registered_order_id = registered_order_id
        order.save()
        async_send_order_email.delay(user_id=order.user.id, order_id=order_id)
    else:
        order.order_status = "Transaction Failed"
        order.save()
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
                        continue
                else:
                    product.stock += order_item.quantity
                    product.save()

    return is_success


    
def kashier_refund(transaction_id, order_id, amount):
    url = f"{KASHIER_REFUND_URL}orders/{order_id}/transactions/{transaction_id}?operation=refund"
    headers = {
        "Content-Type": "application/json",
        "Authorization": KASHIER_SECRET_KEY,
        "accept": "application/json",
    }
    try:
        response = json.loads(
            requests.put(url, json={"amount": amount}, headers=headers).content.decode(
                "utf-8"
            )
        )
        if (
            response["response"]["status"] == "SUCCESS"
            or response["response"]["status"] == "PENDING"
        ):
            return True
        else:
            return response["response"]["status"]
    except Exception as e:
        return "Something went wrong with the payment."
