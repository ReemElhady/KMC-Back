import datetime
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import get_language_from_request
from rest_framework.exceptions import NotAcceptable

from cart.models import Cart
from coupon.views.coupon_views import apply_coupon
from order.models.order_models import Order, OrderItem, OrderAddress
from smsa.smsa import SMSAIntegration
from user.models.user_address import UserAddress


def create_order(request, payment_method):
    with transaction.atomic():
        cart = Cart.objects.calculate_price(request.user)
        cart_item = cart.cart_items_cart.all()
        cart_quantity_errors = check_cart_quantity_in_stock(cart_item, request)
        if len(cart_quantity_errors):
            raise NotAcceptable(
                {"error": "Out of stock", "message": cart_quantity_errors}
            )
        total_price = cart.total_price
        price_paid = total_price

        discount = 0.0
        if cart.coupon:
            coupon, response_code = apply_coupon(
                cart, cart.cart_items_cart.all(), request.user, "en", cart.coupon
            )
            discount = coupon["discount_value"]

        if cart.discount_percentage:
            price_paid -= (cart.discount_percentage / 100) * total_price

        # if request.data.get('points') > 0:
        #     points = use_points(int(request.data.get('points')), request.user)
        #     if points == 'Inapplicable':
        #         raise NotAcceptable('Points must be a multiple of 1000')
        # else:
        #     points = 0
        # price_paid = total_price - points
        if price_paid < 0:
            price_paid = 0
        tax=0
        if cart.tax is not None:
            tax = round(total_price * (cart.tax / 100), 2)
        
        # calculate total order weight
        order_weight = cart.total_weight
        address = get_object_or_404(
            UserAddress, user=request.user, id=request.data["address"]
        )

        shipping_details = SMSAIntegration.calculate_shipping_price(
            cart.total_price,
            discount,
            cart.total_weight,
            address.city.id,
        )

        cod_cost = 0
        if payment_method == "Cash On Delivery":
            cod_cost = shipping_details["cod_cost"]

        shipping_fees = float(shipping_details["shipping_cost"] + cod_cost)

        total_price += shipping_fees
        price_paid += shipping_fees

        order = Order(
            user=request.user,
            coupon=cart.coupon,
            order_status="Ordered",
            payment_type=payment_method,
            total_price=total_price,
            discount=discount,
            tax_value=tax,
            price_paid=price_paid,
            order_weight=order_weight,
            shipping_fees=shipping_fees,
            number_of_boxes=cart.total_number_of_boxes,
        )
        order.save()
        order_items = []
        for order_item in cart_item:
            arabic_title = order_item.product.translations.filter(
                language="ar", field="title"
            ).first()
            if arabic_title:
                arabic_title = arabic_title.text
            product_item_type = None
            product_item_title = None
            product_item_id = None
            if order_item.product_item:
                product_item_type = order_item.product.product_item_title
                product_item_title = order_item.product_item.species
                product_item_id = order_item.product_item.id
                order_item.product_item.stock -= order_item.quantity
                order_item.product_item.save()

            item = OrderItem(
                order=order,
                product_title_en=order_item.product.title,
                product_title_ar=arabic_title,
                product_image=order_item.product.product_image.get(is_main=True).image,
                quantity=order_item.quantity,
                price=(
                    order_item.product.price
                    if not order_item.product.sale_price
                    else order_item.product.sale_price
                ),
                status="Ordered",
                product_uuid=order_item.product.id,
                product_item_type=product_item_type,
                product_item_id=product_item_id,
                product_item_title=product_item_title,
                product_item_weight=order_item.product.weight,
            )
            order_item.product.stock -= order_item.quantity
            order_item.product.save()
            order_items.append(item)
        OrderItem.objects.bulk_create(order_items)
        address = get_object_or_404(
            UserAddress, user=request.user, id=request.data["address"]
        )

        OrderAddress.objects.create(
            order=order,
            name=address.name,
            phone=address.phone,
            phone_country_code=address.phone_country_code,
            country=address.country,
            city=address.city.name,
            address=address.address,
            building=address.building,
            floor=address.floor,
            apartment=address.apartment,
        ).save()
        order = (
            Order.objects.prefetch_related("order_address", "order_item")
            .select_related("user", "coupon")
            .get(id=order.id)
        )

        # Create shipment
        awb = SMSAIntegration.create_shipment(order)
        if awb:
            order.awb = awb
            order.save()
        return order


def check_cart_quantity_in_stock(cart_items, request):
    lang = get_language_from_request(request)
    cart_out_of_stock = []
    for item in cart_items:
        title = item.product.title
        if lang == "ar":
            arabic_translate_obj = item.product.translations.filter(
                language="ar", field="title"
            ).first()
            if arabic_translate_obj:
                title = arabic_translate_obj.text
        if item.product_item:
            stock = item.product_item.stock
        else:
            stock = item.product.stock
        if item.quantity > stock:
            cart_out_of_stock.append(
                {
                    "title": title,
                    "image": item.product.product_image.get(is_main=True).image.url,
                }
            )
    return cart_out_of_stock


def can_refund(order: Order) -> bool:

    if (
        order.order_status
        not in [
            "Paid",
            "Shipped",
            "Completed",
            "Partially Refunded",
            "Refund requested",
        ]
        or not order.compelted_at
        or order.price_paid < order.total_price
    ):
        return False
    date = datetime.datetime.today() - datetime.timedelta(days=15)
    if order.compelted_at:
        if order.compelted_at <= date.date():
            return False
    order_all_items = order.order_item.filter(order=order)

    from django.db.models import Q

    if (
        order_all_items.count()
        == order_all_items.filter(
            Q(status="Refunded") | Q(status="Refund Requested")
        ).count()
    ):
        return False

    return True


def get_order_expired_at(created_at):
    return created_at + timedelta(minutes=settings.ORDER_EXPIRES_AFTER_IN_HOURS)


def can_be_paid(order):
    return (
        get_order_expired_at(order.created_at) >= timezone.now()
        and order.order_status == "Awaiting Payment"
        and order.payment_type == "Credit Card"
    )
