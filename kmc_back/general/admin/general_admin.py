from django.contrib import admin

from general.models.general_model import General


@admin.register(General)
class GeneralAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not General.objects.exists()

    list_display = (
        "tax_percentage",
        # "point_value",
    )
    exclude = ("point_value",)
