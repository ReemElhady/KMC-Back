from django.urls import path
from order.views.order_apis import (
    CreateOrderAPI,
    PayMobCallBack,
    ReOrderAPI,
    ShipmentStatus,
    PayOrderAPI,
)
from order.views.refund_apis import RefundAPI

urlpatterns = [
    path("", CreateOrderAPI.as_view()),
    path("<int:pk>", CreateOrderAPI.as_view()),
    path("pay-order/<int:order_id>/", PayOrderAPI.as_view()),
    path("payment-callback/", PayMobCallBack.as_view()),
    path("refund/", RefundAPI.as_view()),
    path("re-order/", ReOrderAPI.as_view()),
    path("re-order/<int:pk>", ReOrderAPI.as_view()),
    path("shipment-status/", ShipmentStatus.as_view()),

]

