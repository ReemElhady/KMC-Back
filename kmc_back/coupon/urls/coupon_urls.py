from django.urls import path

from ..views.coupon_views import CouponAPI

urlpatterns = [
    path('', CouponAPI.as_view(), name='coupon-view')
]
