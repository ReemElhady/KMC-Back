from django.contrib import admin

from ..models.coupon_models import Coupon


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'expire_date', ]
    search_fields = ['code', 'discount_percentage']
    list_filter = ['discount_percentage', 'users']
    ordering = ('-discount_percentage', 'expire_date')


admin.site.register(Coupon, CouponAdmin)
