from django.contrib import admin
from user.models.user_address import UserAddress


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        "user_name",
        "name",
        "address",
        "country",
        "city",
        "phone",
    )
    list_filter = (
        "country",
        "city",
        ("user__name", custom_titled_filter("user name")),
        ("user__email", custom_titled_filter("user email")),
        ("user__phone", custom_titled_filter("user phone")),
        "address",
        "name",
        "phone",
        "building",
        "floor",
        "apartment",
        "is_default",
    )

    search_fields = ["name", "phone", "address"]

    ordering = ["-id"]

    def user_name(self, obj):
        user = obj.user
        return f"{user.name} ({user.phone})"
