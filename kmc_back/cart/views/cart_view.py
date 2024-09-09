from django.shortcuts import get_object_or_404
from django.utils import translation
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from cart.helpers.utility import return_cart_summary
from cart.models.cart_models import Cart, CartItem
from cart.serializers.cart_serializer import (
    CardItemSerializer,
    UpdateCartItems,
    CartSerializer,
    GuestItemsSerialzier,
    SingleGuestItemSerializer,
)
from product.models.product_models import Product, ProductItem


def get_or_create_cart(user, data):
    return Cart.objects.get_or_create(user=user, defaults=data)[0]


class CartApiView(ViewSet):
    permission_classes = [
        IsAuthenticated,
    ]

    def add_to_cart(self, request, product_id, quantity, product_item=None):
        if quantity > 0:
            product = get_object_or_404(Product, id=product_id)
            if product.weight == 0.0:
                return Response(
                    {"error": "weight must be grater than 0.0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if quantity > product.stock:
                return Response(
                    {"error": "quantity is out of stock"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart = get_or_create_cart(
                user=request.user, data={"user": request.user, "coupon": None}
            )
            if product_item:
                product_item = get_object_or_404(ProductItem, id=product_item)

                try:
                    cart_item = CartItem.objects.get(
                        cart=cart, product=product, product_item=product_item
                    )
                    if quantity + cart_item.quantity > cart_item.product_item.stock:
                        return Response(
                            {"error": "quantity is out of stock"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    cart_item.quantity = cart_item.quantity + quantity
                    cart_item.save()
                except:
                    if quantity > product_item.stock:
                        return Response(
                            {"error": "quantity is out of stock"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    cart_item = CartItem.objects.create(
                        product=product,
                        cart=cart,
                        quantity=quantity,
                        product_item=product_item,
                    )
            else:

                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    if cart_item.quantity + quantity > product.stock:
                        return Response(
                            {"error": "quantity is out of stock"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    cart_item.quantity = cart_item.quantity + quantity
                    cart_item.save()
                except:
                    cart_item = CartItem.objects.create(
                        product=product, cart=cart, quantity=quantity
                    )
            query = Cart.objects.calculate_price(request.user)
            calculation = return_cart_summary(
                query.total_price, query.tax, query.discount_percentage
            )
            lang = translation.get_language_from_request(request)
            serilaizer = CardItemSerializer(cart_item, context={"lang": lang})
            return Response(
                {"item": serilaizer.data, "order_summary": calculation},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "quantity must be 1 or more"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def cart_list(self, request):
        # try:
        lang = translation.get_language_from_request(request)
        cart = Cart.objects.calculate_price(request.user)
        if cart is None:
            return Response(
                {"cart": [], "order_summary": "", "message": "No items in cart"},
                status=status.HTTP_200_OK,
            )
        calculation = return_cart_summary(
            cart.total_price,
            cart.tax,
            cart.discount_percentage,
        )
        serilaizer = CartSerializer(cart, context={"lang": lang})
        return Response(
            {"cart": serilaizer.data, "order_summary": calculation},
            status=status.HTTP_200_OK,
        )
        # except Exception as e:
        #     return Response({"cart": [], "order_summary": None, 'exception': str(e)}, status=status.HTTP_200_OK)

    def update_cart_items(self, request):
        serializer = UpdateCartItems(data={"items": request.data})
        if serializer.is_valid():
            items_to_update = []
            errors = []
            lang = translation.get_language_from_request(request)
            cart = get_object_or_404(Cart, user=request.user)
            for item in serializer.validated_data.get("items"):
                saved_item = get_object_or_404(
                    CartItem, id=item.get("item_id"), cart=cart
                )
                if saved_item.product_item:
                    if item["quantity"] > saved_item.product_item.stock:
                        errors.append(
                            {
                                "error": {
                                    "item_id": saved_item.id,
                                    "message": "quantity is  out of stock",
                                }
                            }
                        )
                        continue
                else:
                    if item["quantity"] > saved_item.product.stock:
                        errors.append(
                            {
                                "error": {
                                    "item_id": saved_item.id,
                                    "message": "quantity is  out of stock",
                                }
                            }
                        )
                        continue
                saved_item.quantity = item["quantity"]
                items_to_update.append(saved_item)
            if errors:
                items_serializers = CartSerializer(cart, context={"lang": lang})

                return Response(
                    {"errors": errors, "cart": items_serializers.data},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            CartItem.objects.bulk_update(items_to_update, ["quantity"])

            cart = Cart.objects.calculate_price(request.user)
            calculation = return_cart_summary(
                cart.total_price,
                cart.tax,
                cart.discount_percentage,
            )

            items_serializers = CartSerializer(cart, context={"lang": lang})

            return Response(
                {"cart": items_serializers.data, "order_summary": calculation},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_item(self, request, item_id):
        cart = Cart.objects.get_cart_or_404(request.user)
        cart_item = cart.cart_items_cart.filter(id=item_id).first()
        if cart_item:
            cart_item.delete()
        if cart.cart_items_cart.count() == 0:
            if cart.coupon:
                cart.coupon = None
                cart.save()
            return Response(
                {"cart": [], "order_summary": None}, status=status.HTTP_200_OK
            )

        cart = Cart.objects.calculate_price(request.user)
        calculation = return_cart_summary(
            cart.total_price, cart.tax, cart.discount_percentage
        )

        return Response(
            {"status": "deleted successfully", "order_summary": calculation},
            status=status.HTTP_200_OK,
        )

    def add_guest_cart_items(self, request):
        serializer = GuestItemsSerialzier(data={"items": request.data})
        lang = translation.get_language_from_request(request)
        if serializer.is_valid():
            quantity_errors = []
            created_items = []
            updated_items = []
            cart = get_or_create_cart(
                user=request.user, data={"user": request.user, "coupon": None}
            )
            for item in serializer.validated_data.get("items"):
                # product = get_object_or_404(Product, id=item["product_id"])
                product = (
                    Product.objects.filter(id=item["product_id"])
                    .translate(lang)
                    .first()
                )
                if product is None:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                title = product.title
                image = product.product_image.filter(is_main=True).first().image.url

                if item["quantity"] > product.stock:
                    quantity_errors.append(
                        {
                            "error": {
                                "product_id": item["product_id"],
                                "title": title,
                                "image": image,
                                "message": "quantity is  out of stock",
                            }
                        }
                    )
                else:
                    try:
                        not_bigger = False
                        if item["product_item_id"]:
                            updated_item = CartItem.objects.get(
                                product=product,
                                cart=cart,
                                product_item_id=item["product_item_id"],
                            )
                            if (
                                updated_item.quantity + item["quantity"]
                            ) > updated_item.product_item.stock:
                                quantity_errors.append(
                                    {
                                        "error": {
                                            "product_id": item["product_id"],
                                            "title": title,
                                            "image": image,
                                            "message": "quantity is  out of stock",
                                        }
                                    }
                                )
                            else:
                                not_bigger = True
                        else:
                            updated_item = CartItem.objects.get(
                                product=product, cart=cart
                            )
                            if (
                                updated_item.quantity + item["quantity"]
                            ) > product.stock:
                                quantity_errors.append(
                                    {
                                        "error": {
                                            "product_id": item["product_id"],
                                            "title": title,
                                            "image": image,
                                            "message": "quantity is  out of stock",
                                        }
                                    }
                                )
                            else:
                                not_bigger = True
                        if not_bigger:
                            updated_item.quantity = (
                                updated_item.quantity + item["quantity"]
                            )
                            updated_items.append(updated_item)
                    except CartItem.DoesNotExist:
                        if item["product_item_id"]:
                            created_item = CartItem(
                                product=product,
                                quantity=item["quantity"],
                                cart=cart,
                                product_item_id=item["product_item_id"],
                            )
                        else:
                            created_item = CartItem(
                                product=product, quantity=item["quantity"], cart=cart
                            )
                        created_items.append(created_item)
            if created_items:
                CartItem.objects.bulk_create(created_items)
            if updated_items:
                CartItem.objects.bulk_update(updated_items, ["quantity"])
            if not created_items and not updated_items and not quantity_errors:
                cart.delete()
                return Response(
                    {"items": [], "order_summary": None, "error": []},
                    status=status.HTTP_200_OK,
                )
            cart = Cart.objects.calculate_price(request.user)
            calculation = return_cart_summary(
                cart.total_price, cart.tax, cart.discount_percentage
            )

            items_serializers = CartSerializer(cart, context={"lang": lang})
            return Response(
                {
                    "cart": items_serializers.data,
                    "order_summary": calculation,
                    "error": quantity_errors,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckQuantityApiView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        serializer = SingleGuestItemSerializer(data=request.data)
        if serializer.is_valid():
            if request.data.get("product_item"):
                product_item = get_object_or_404(
                    ProductItem, id=request.data.get("product_item")
                )
                if serializer.validated_data.get("quantity") > product_item.stock:
                    return Response(
                        {"error": "quantity is  out of stock"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(
                        {"ok": "quantity is valid"}, status=status.HTTP_200_OK
                    )
            else:
                product = get_object_or_404(
                    Product, id=serializer.validated_data.get("product_id")
                )
                if serializer.validated_data.get("quantity") > product.stock:
                    return Response(
                        {"error": "quantity is  out of stock"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(
                        {"ok": "quantity is valid"}, status=status.HTTP_200_OK
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
