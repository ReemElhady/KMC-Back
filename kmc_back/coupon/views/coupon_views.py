import datetime

from django.utils.translation import get_language_from_request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.helpers.utility import return_cart_summary
from coupon.helpers.coupon_response import coupon_error_message

def apply_coupon(cart, cart_items, user, lang="en", coupon=None):
    if not cart or not cart_items.exists():
        return {
            "error": coupon_error_message["no_items"][lang]
        }, status.HTTP_404_NOT_FOUND

    total_price = cart.total_price  # Total price of the cart (before discount)
    eligible_products_price = 0  # Total price of eligible products
    discount_value = 0  # Total discount amount for eligible products

    # Validate eligible products for the coupon
    if coupon.products.exists():
        product_ids = [item.product.id for item in cart_items]
        eligible_products = coupon.products.filter(id__in=product_ids)

        if not eligible_products.exists():
            return {
                "error": coupon_error_message["invalid_product_coupon"][lang]
            }, status.HTTP_403_FORBIDDEN

        # Calculate total price and discount for eligible products
        for item in cart_items:
            if item.product.id in eligible_products.values_list("id", flat=True):
                item_price = item.product.get_final_price() * item.quantity
                eligible_products_price += item_price
                discount_value += item_price * (coupon.discount_percentage / 100)
    else:
        # If no specific products are tied to the coupon, consider the entire cart eligible
        eligible_products_price = total_price
        discount_value = total_price * (coupon.discount_percentage / 100)

    # Validate private coupons
    coupon_users = coupon.users.all()
    if coupon_users and user not in coupon_users:
        return {
            "error": coupon_error_message["invalid_coupon"][lang]
        }, status.HTTP_403_FORBIDDEN

    # Validate if the coupon is expired
    if datetime.date.today() >= coupon.expire_date:
        return {
            "error": coupon_error_message["expired_coupon"][lang]
        }, status.HTTP_403_FORBIDDEN

    # Validate the minimum value to apply the coupon
    if coupon.min_value_to_apply > 0 and eligible_products_price < coupon.min_value_to_apply:
        return {
            "error": coupon_error_message["minimum_coupon"][lang]
            + str(coupon.min_value_to_apply)
        }, status.HTTP_403_FORBIDDEN

    # Apply the max discount value if applicable
    if 0 < coupon.max_discount_value < discount_value:
        discount_value = coupon.max_discount_value

    # Calculate the discount percentage (relative to the total cart price)
    discount_percent = (discount_value / total_price) * 100 if total_price > 0 else 0

    # Apply the coupon to the cart
    cart.coupon = coupon
    cart.save()

    # Ensure all required fields are included in the return context
    return {
        "tax": cart.tax,
        "total_price": total_price,
        "discount": discount_percent,
        "discount_value": discount_value,
    }, status.HTTP_200_OK


# def apply_coupon(cart, cart_items, user, lang="en", coupon=None):
#     if not cart or not cart_items.exists():
#         return {
#             "error": coupon_error_message["no_items"][lang]
#         }, status.HTTP_404_NOT_FOUND

#     total_price = cart.total_price

#     # Validate eligible products for the coupon
#     eligible_products_price = 0  # Total price of eligible products
#     eligible_discount = 0  # Total discount amount for eligible products

#     if coupon.products.exists():
#         product_ids = [item.product.id for item in cart_items]
#         eligible_products = coupon.products.filter(id__in=product_ids)

#         if not eligible_products.exists():
#             return {
#                 "error": coupon_error_message["invalid_product_coupon"][lang]
#             }, status.HTTP_403_FORBIDDEN

#         # Calculate discount for eligible products only
#         for item in cart_items:
#             if item.product.id in eligible_products.values_list("id", flat=True):
#                 item_price = item.product.get_final_price() * item.quantity
#                 eligible_products_price += item_price
#                 eligible_discount += item_price * (coupon.discount_percentage / 100)

#     # Validate private coupons
#     coupon_users = coupon.users.all()
#     if coupon_users and user not in coupon_users:
#         return {
#             "error": coupon_error_message["invalid_coupon"][lang]
#         }, status.HTTP_403_FORBIDDEN

#     # Validate if the coupon is expired
#     if datetime.date.today() >= coupon.expire_date:
#         return {
#             "error": coupon_error_message["expired_coupon"][lang]
#         }, status.HTTP_403_FORBIDDEN

#     # Validate the minimum value to apply the coupon
#     if coupon.min_value_to_apply > 0 and eligible_products_price < coupon.min_value_to_apply:
#         return {
#             "error": coupon_error_message["minimum_coupon"][lang]
#             + str(coupon.min_value_to_apply)
#         }, status.HTTP_403_FORBIDDEN

#     # Apply the max discount value if applicable
#     if 0 < coupon.max_discount_value < eligible_discount:
#         eligible_discount = coupon.max_discount_value

#     # Apply the coupon to the cart
#     cart.coupon = coupon
#     cart.save()

#     # Total cart price after discount (only eligible products are discounted)
#     final_total_price = total_price - eligible_discount

#     return {
#         "tax": cart.tax,
#         "total_price": final_total_price,
#         "eligible_products_price": eligible_products_price,
#         "discount_value": eligible_discount,
#     }, status.HTTP_200_OK

# def apply_coupon(cart, cart_items, user, lang="en", coupon=None):
#     if not cart or not cart_items.exists():
#         return {
#             "error": coupon_error_message["no_items"][lang]
#         }, status.HTTP_404_NOT_FOUND
#     total_price = cart.total_price

#     # for Private Coupon
#     coupon_users = coupon.users.all()
#     # if this coupon is private
#     if coupon_users and user not in coupon_users:
#         # if this coupon is available for authenticated user
#         return {
#             "error": coupon_error_message["invalid_coupon"][lang]
#         }, status.HTTP_403_FORBIDDEN

#     # if coupon is expired
#     if datetime.date.today() >= coupon.expire_date:
#         return {
#             "error": coupon_error_message["expired_coupon"][lang]
#         }, status.HTTP_403_FORBIDDEN
#     # if minimum value to apply this coupon exceeds the total price of the cart
#     if coupon.min_value_to_apply > 0 and total_price < coupon.min_value_to_apply:
#         return {
#             "error": coupon_error_message["minimum_coupon"][lang]
#             + coupon.min_value_to_apply
#         }, status.HTTP_403_FORBIDDEN

#     # if cart discount exceeds the coupon maximum discount

#     discount_percent = coupon.discount_percentage
#     discount = total_price * (discount_percent / 100)

#     if 0 < coupon.max_discount_value < discount:
#         discount = coupon.max_discount_value
#         discount_percent = (discount / total_price) * 100
#     # setting coupon and save it in authenticated user's cart
#     cart.coupon = coupon
#     cart.save()
#     return {
#         "tax": cart.tax,
#         "total_price": total_price,
#         "discount": discount_percent,
#         "discount_value": discount,
#     }, status.HTTP_200_OK


class CouponAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from cart.models.cart_models import Cart, Coupon

        lang = get_language_from_request(request)
        cart = Cart.objects.calculate_price(user=request.user)
        if cart.coupon:
            return Response(
                {"error": coupon_error_message["already_applied"][lang]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_items = cart.cart_items_cart.all()
        
        
        coupon = Coupon.objects.filter(code=request.data.get("code")).first()   
        if coupon:
            response, response_code = apply_coupon(
                cart, cart_items, request.user, lang, coupon
            )
            if response_code == status.HTTP_200_OK:
                response = return_cart_summary(
                    response.get("total_price"),
                    response.get("tax"),
                    response.get("discount"),
                )
        else:
            return Response(
                {"error": coupon_error_message["invalid_coupon"][lang]},
                status.HTTP_404_NOT_FOUND,
            )
        return Response(response, response_code)

    def delete(self, request, format=None):
        from cart.models.cart_models import Cart

        cart = Cart.objects.filter(user=request.user)
        if cart.exists():
            cart.update(coupon=None)
            cart = Cart.objects.calculate_price(request.user)
            calculation = return_cart_summary(
                cart.total_price, cart.tax, cart.discount_percentage
            )
            return Response(calculation, status=status.HTTP_200_OK)
        return Response(
            {"message": "Something has occurred"}, status=status.HTTP_400_BAD_REQUEST
        )
