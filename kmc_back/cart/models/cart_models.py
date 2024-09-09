from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from cart.models.cart_manager import CartManager
from coupon.models.coupon_models import Coupon
from product.models.product_models import Product, ProductItem


class Cart(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='cart_user')
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True, related_name='cart_coupon', blank=True)

    objects = CartManager()

    class Meta:
        verbose_name_plural = "User cart"

    def __str__(self) -> str:
        user = self.user
        return f"{user.name}({user.phone})"


class CartItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='cart_items_product')
    product_item = models.ForeignKey(
        ProductItem, on_delete=models.CASCADE, related_name='cart_items_product_item', null=True, blank=True)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items_cart')

    class Meta:
        unique_together = (("product", "cart", 'product_item'),)
        verbose_name_plural = "user cart items"

    def __str__(self) -> str:
        return self.product.title
