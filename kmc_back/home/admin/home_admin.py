from django.contrib import admin

from ..models import PopularProduct, LowStockProduct
from ..models.home_models import HomeSwiper, HomeDetails, Ad, FlashSale, GalleryImage, DemoBooking, DemoBookingPage



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

@admin.register(LowStockProduct)
class LowStockProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return LowStockProduct.objects.count() < 3
admin.site.register(Ad)

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'created_at')
    list_filter = ('created_at',)



@admin.register(DemoBooking)
class DemoBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name','email','phone','device_name','date','time', 'created_at')
    list_filter = ('created_at',)




class DemoBookingPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not DemoBookingPage.objects.exists()

admin.site.register(DemoBookingPage,DemoBookingPageAdmin)