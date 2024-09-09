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
    total_price = cart.total_price

    # for Private Coupon
    coupon_users = coupon.users.all()
    # if this coupon is private
    if coupon_users and user not in coupon_users:
        # if this coupon is available for authenticated user
        return {
            "error": coupon_error_message["invalid_coupon"][lang]
        }, status.HTTP_403_FORBIDDEN

    # if coupon is expired
    if datetime.date.today() >= coupon.expire_date:
        return {
            "error": coupon_error_message["expired_coupon"][lang]
        }, status.HTTP_403_FORBIDDEN
    # if minimum value to apply this coupon exceeds the total price of the cart
    if coupon.min_value_to_apply > 0 and total_price < coupon.min_value_to_apply:
        return {
            "error": coupon_error_message["minimum_coupon"][lang]
            + coupon.min_value_to_apply
        }, status.HTTP_403_FORBIDDEN

    # if cart discount exceeds the coupon maximum discount

    discount_percent = coupon.discount_percentage
    discount = total_price * (discount_percent / 100)

    if 0 < coupon.max_discount_value < discount:
        discount = coupon.max_discount_value
        discount_percent = (discount / total_price) * 100
    # setting coupon and save it in authenticated user's cart
    cart.coupon = coupon
    cart.save()
    return {
        "tax": cart.tax,
        "total_price": total_price,
        "discount": discount_percent,
        "discount_value": discount,
    }, status.HTTP_200_OK


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
