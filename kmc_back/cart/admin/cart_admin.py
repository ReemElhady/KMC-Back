from django.contrib import admin

from cart.models.cart_models import Cart, CartItem


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "coupon",
    )
    list_filter = (

        ("user__name", custom_titled_filter("user name")),
        ("user__phone", custom_titled_filter("branch phone")),
        "coupon",
    )
    search_fields = ['user__name', 'user__name', 'coupon']


class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity",
        "cart",
    )
    list_filter = (

        ("product__type__name", custom_titled_filter("type")),
        ("product__title", custom_titled_filter("product title")),
        ("product__brand__name", custom_titled_filter("brand name")),
        ("product__branch__name", custom_titled_filter("branch name")),
        ("product__sub_branch__name", custom_titled_filter("subbranch name")),
    )
    search_fields = ['product__title', 'product__brand__name', 'product__type__name', 'product__branch__name',
                     'product__sub_branch__name', 'quantity']


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
