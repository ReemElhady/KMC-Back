from django.contrib import admin

from smsa.models import Zone, ZoneCity, ShippingFees

class ZoneCityInline(admin.StackedInline):
    model = ZoneCity
    extra = 1

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    inlines = (
        ZoneCityInline,
    )


@admin.register(ZoneCity)
class ZoneCityAdmin(admin.ModelAdmin):
    pass

admin.site.register(ShippingFees)