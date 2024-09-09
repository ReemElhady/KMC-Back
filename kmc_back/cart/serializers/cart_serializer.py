from rest_framework import serializers

from cart.models.cart_models import Cart, CartItem
from product.models.product_models import Product, ProductItem
from product.serializer.product_serializers import ProductItemSerializer


class ProductSerilaizer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()

    def get_main_image(self, obj):
        try:
            return obj.product_image.get(is_main=True).image.url
        except:
            return "doesn't exists"

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "main_image",
            "price",
            "sale_price"
        ]


class CardItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    out_of_stock = serializers.SerializerMethodField()
    product_item = serializers.SerializerMethodField()

    def get_out_of_stock(self, obj):
        return obj.quantity > obj.product.stock

    def get_product(self, obj):
        lang = self.context.get('lang')
        product = Product.objects.translate(lang).get(id=obj.product.id)
        return ProductSerilaizer(product).data

    def get_product_item(self, obj):
        if obj.product_item:
            lang = self.context.get('lang')
            product = ProductItem.objects.translate(lang).get(id=obj.product_item.id)
            return ProductItemSerializer(product).data
        return {}

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "out_of_stock",
            "product_item"
        ]
        read_only_fields = ["id", ]


class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    coupon_code = serializers.SerializerMethodField

    def get_cart_items(self, obj):
        lang = self.context.get('lang')
        return CardItemSerializer(obj.cart_items_cart, many=True, context={"lang": lang}).data

    def get_coupon_code(self, obj):
        if obj.coupon:
            return obj.coupon.code
        return None

    class Meta:
        model = Cart
        fields = [
            "coupon",
            "cart_items"
        ]


class singleUpdateCartItem(serializers.Serializer):
    item_id = serializers.IntegerField(min_value=0)
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItems(serializers.Serializer):
    items = singleUpdateCartItem(many=True)


class SingleGuestItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    product_item_id = serializers.IntegerField(allow_null=True, required=False)
    quantity = serializers.IntegerField(min_value=1)


class GuestItemsSerialzier(serializers.Serializer):
    items = SingleGuestItemSerializer(many=True)
