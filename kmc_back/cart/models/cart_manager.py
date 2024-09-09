from django.db.models import Manager, Sum, Case, When, F, FloatField, Subquery
from django.http import Http404
from rest_framework import status

from coupon.views.coupon_views import apply_coupon
from general.models.general_model import General


class CartManager(Manager):
    def calculate_price(self, user):
        cart = (
            self.filter(user=user)
            .select_related("coupon")
            .prefetch_related(
                "cart_items_cart", "cart_items_cart__product", "coupon__users"
            )
            .annotate(
                total_price=Sum(
                    Case(
                        When(
                            cart_items_cart__product__sale_price__gt=0,
                            then=F("cart_items_cart__product__sale_price"),
                        ),
                        default=F("cart_items_cart__product__price"),
                    )
                    * F("cart_items_cart__quantity"),
                    output_field=FloatField(),
                ),
                tax=Subquery(General.objects.all().values("tax_percentage")[:1]),
                discount_percentage=F("coupon__discount_percentage"),
                total_weight=Sum(
                    F("cart_items_cart__product__weight")
                    * F("cart_items_cart__quantity"),
                    output_field=FloatField(),
                ),
                total_number_of_boxes=Sum(
                    F("cart_items_cart__product__number_of_boxes")
                    * F("cart_items_cart__quantity"),
                    output_field=FloatField(),
                ),
            )
        )
        cart = cart.first()
        if cart is None:
            return cart
        if cart.coupon:
            response, response_code = apply_coupon(
                cart, cart.cart_items_cart.all(), user, "en", cart.coupon
            )

            cart.discount_percentage = response["discount"]
            if response_code != status.HTTP_200_OK:
                cart.discount_percentage = 0
                cart.coupon = None
                cart.save()
        return cart

    def get_cart_or_404(self, user):
        try:
            query = self.prefetch_related("cart_items_cart").get(user=user)
            return query
        except self.model.DoesNotExist:
            return Http404("No Cart matches the given query.")
