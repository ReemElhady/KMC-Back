from django.contrib import admin

from ..models import PopularProduct
from ..models.home_models import HomeSwiper, HomeDetails


class HomeSwiperAdmin(admin.ModelAdmin):
    pass


class HomeDetailsAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not HomeDetails.objects.exists()


admin.site.register(HomeSwiper, HomeSwiperAdmin)
admin.site.register(HomeDetails, HomeDetailsAdmin)


@admin.register(PopularProduct)
class PopularProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return PopularProduct.objects.count() < 8
