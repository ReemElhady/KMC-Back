from django.urls import path

from user.views.user_address_view import CreateUserAddressAPI

urlpatterns = [
    path("", CreateUserAddressAPI.as_view({
        'get': 'addresses_list',
        'post': 'create_address'
    }), name="userAddressActionCreateGet"),
    path("<int:addressId>", CreateUserAddressAPI.as_view(
        {'put': 'update_address',
         'delete': 'delete_address',
         'patch': 'mark_address_as_default'
         }), name="userAddressActionUpdateAndDelete"),

]
