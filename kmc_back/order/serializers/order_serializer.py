from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from order.models.order_models import Order, OrderItem, OrderAddress
from order.models.refund_models import RefundItem
from order.utility.order_utility import can_refund, get_order_expired_at, can_be_paid


class RefundSerializer(serializers.Serializer):
    requested_quantity = serializers.IntegerField()
    refunded_quantity = serializers.IntegerField()
    reason = serializers.CharField()


class OrderItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order = serializers.CharField(source="order.code")
    product_title_en = serializers.CharField()
    product_title_ar = serializers.CharField()
    product_image = serializers.FileField()
    quantity = serializers.IntegerField()
    price = serializers.FloatField()
    total_price = serializers.SerializerMethodField()
    status = serializers.CharField()
    product_item_type = serializers.CharField()
    product_item_title = serializers.CharField()
    refund_item = serializers.SerializerMethodField()

    def get_refund_item(self, obj):
        return RefundSerializer(
            RefundItem.objects.select_related("refund")
            .filter(refund__order_id=obj.order_id, order_item_id=obj.id)
            .first()
        ).data

    def get_total_price(self, obj):
        return obj.price * obj.quantity


class OrderAddressSerializer(serializers.Serializer):
    order = serializers.CharField(source="order.code")
    name = serializers.CharField()
    phone = serializers.CharField()
    phone_country_code = serializers.CharField()
    country = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()


class OrderSerializer(serializers.ModelSerializer):
    # items = OrderItemListSerializer(source='order_item', many=True)
    items = serializers.SerializerMethodField()
    user = serializers.CharField(source="user.name")
    address = serializers.SerializerMethodField()
    refundable = serializers.SerializerMethodField()
    expires_after = serializers.SerializerMethodField()
    can_be_paid = serializers.SerializerMethodField()
    # can_refund = serializers.SerializerMethodField()

    def get_refundable(self, obj):
        return can_refund(obj)

    def get_items(self, obj):
        items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemListSerializer(items, many=True)
        return serializer.data

    def get_address(self, obj):
        address = get_object_or_404(OrderAddress, order=obj)
        serializer = OrderAddressSerializer(address)
        return serializer.data

    def get_expires_after(self, obj):
        return settings.ORDER_EXPIRES_AFTER_IN_HOURS

    def get_can_be_paid(self, obj):
        return can_be_paid(obj)

    class Meta:
        model = Order
        fields = "__all__"
        
        
