from django.urls import path

from cart.views.cart_view import CartApiView, CheckQuantityApiView

urlpatterns = [
    path("", CartApiView.as_view({
        'get': 'cart_list',
        'patch': 'update_cart_items',
        'post': 'add_guest_cart_items'
    }), name="cartItemList"),
    path("<int:item_id>", CartApiView.as_view({'delete': "delete_item"}), name="deleteItemFromCart"),
    path("add-to-cart/<uuid:product_id>/<int:quantity>", CartApiView.as_view({'get': 'add_to_cart'}),
         name="addItemToCart"),
    path("add-to-cart/<uuid:product_id>/<int:quantity>/<int:product_item>", CartApiView.as_view({'get': 'add_to_cart'}),
         name="addItemToCart"),
    path("check-quantity", CheckQuantityApiView.as_view(), name="checkItemQuntity"),

]
