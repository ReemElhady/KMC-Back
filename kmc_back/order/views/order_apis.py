from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import get_language_from_request
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from cart.helpers.utility import return_cart_summary
from cart.models import Cart, CartItem
from cart.serializers.cart_serializer import CartSerializer
from common.tasks import async_send_email
from order.models.order_models import Order, OrderItem
from order.payment.payment import kashier_base_callback, kashier_generate_iframe
from order.serializers.order_serializer import OrderSerializer 
from order.tasks import async_send_order_email
from order.utility.order_utility import create_order
from smsa.smsa import SMSAIntegration
from product.models import Product, ProductItem

class CreateOrderAPI(CreateAPIView, ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.kwargs.get("pk"):
            return (
                Order.objects.filter(user=self.request.user, id=self.kwargs.get("pk"))
                .prefetch_related("order_item")
                .order_by("-id")
            )
        else:
            return (
                Order.objects.filter(user=self.request.user)
                .prefetch_related("order_item")
                .order_by("-id")
            )

    def create(self, request, *args, **kwargs):
        try:
            if request.data["payment_method"] == "Cash On Delivery":
                order = create_order(request, "Cash On Delivery")
                if order.price_paid == 0:
                    order.order_status = "Paid"
                order.shipping_status = "Preparing for Delivery"
                order.save()
                
                async_send_email.delay(
                    subject="New order",
                    message=f"New order by {order.user.name}, Phone {order.user.phone}, Awb: {order.awb}",
                    receivers=[
                        "mazen@kandilmedical.com",
                        "ahmed@kandilmedical.com",
                        "Karim@kandilmedical.com",
                    ],
                )
    
                async_send_order_email.delay(order.user.id, order.id)
   
                serializer = OrderSerializer(order).data
                return_status = (
                    {"success": True, "order": serializer},
                    HTTP_201_CREATED,
                )
            else:
                order = create_order(request, "Credit Card")
                order.order_status = "Awaiting Payment"
                order.save()
                serializer = OrderSerializer(order).data
                # if order.price_paid == 0:
                #     order.order_status = "Paid"
                #     order.shipping_status = "Preparing for Delivery"
                #     order.save(update_fields=["order_status", "shipping_status"])

                #     async_send_order_email.delay(order.user.id, order.id)
                #     return_status = (
                #         {"success": True, "order": serializer, "is_points": True},
                #         HTTP_201_CREATED,
                #     )
            # else:
                iframe_url = kashier_generate_iframe(order)
                return_status = (
                    {"iframe_url": iframe_url},
                    HTTP_201_CREATED,
                )
                
            Cart.objects.filter(user=request.user).delete()
            return Response(*return_status)
        except Exception as exception:
            return Response(
                {"message": "An error has occurred", "exception": str(exception)},
                status=HTTP_400_BAD_REQUEST,
            )

class PayMobCallBack(APIView):
    permission_classes = []

    def get(self, request):
        params = request.query_params
        is_success = params.get("paymentStatus")
        call_back = (
            kashier_base_callback(
                params.get("merchantOrderId"),
                "true",
                params.get("transactionId"),
                params.get("orderId"),
            )
            if is_success == "SUCCESS"
            else kashier_base_callback(
                params.get("merchantOrderId"),
                "false",
                params.get("transactionId"),
                params.get("orderId"),
            )
        )
        return redirect(
            f"https://www.kandilmedical.com/account/orders?is_success={call_back}"
            # f"http://localhost:4200/account/orders/?is_success={call_back}"
        )


class PayOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
            order_status="Awaiting Payment",
            payment_type="Credit Card",
        )
        return Response(kashier_generate_iframe(order), status=HTTP_200_OK)


class ShipmentStatus(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).exclude(shipping_status="Delivered")
        orders_list = []
        for order in orders:
            response = SMSAIntegration.query_shipping_status(order.awb)
            if response:
                if response["isDelivered"]:
                    order.order_status = "Completed"
                    order.shipping_status = "Delivered"
                    continue
                scans = response["Scans"]
                sorted_scans = sorted(scans, key=lambda scan: scan["ScanDateTime"])
                order.shipping_status = sorted_scans[0]["ScanDescription"]
                orders_list.append(order)

        Order.objects.bulk_update(
            orders_list, fields=["shipping_status", "order_status"]
        )

        return Response({"message": "Orders status updated"}, status=HTTP_200_OK)



# class ReOrderAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk=None):
#         # Clear the existing cart items
#         CartItem.objects.filter(cart__user=request.user).delete()
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         lang = get_language_from_request(request)
#         order = get_object_or_404(Order, id=pk)
#         order_items = OrderItem.objects.filter(order=order)
#         cart_items = []
        
#         try:
#             for order_item in order_items:
#                 if order_item.product_item_id:  # Check if there's a specific variant
#                     product_item = get_object_or_404(ProductItem, id=order_item.product_item_id)
                    
#                     # Check if the stock of the product item is sufficient
#                     if product_item.stock < order_item.quantity:
#                         return Response(
#                             {"message": f"Insufficient stock for {product_item.product.title} - {product_item.variant_name}"},
#                             status=HTTP_400_BAD_REQUEST
#                         )
                    
#                     item = CartItem(
#                         product=product_item.product,  # Set the main product
#                         product_item=product_item,  # Set the variant
#                         quantity=order_item.quantity,
#                         cart=cart,
#                     )
#                     product_item.stock -= order_item.quantity  # Deduct the stock from the variant
#                     product_item.save()

#                 else:
#                     product = order_item.product
#                     # Check if the stock of the product is sufficient
#                     if product.stock < order_item.quantity:
#                         return Response(
#                             {"message": f"Insufficient stock for {product.title}"},
#                             status=HTTP_400_BAD_REQUEST
#                         )
                    
#                     item = CartItem(
#                         product=product,
#                         quantity=order_item.quantity,
#                         cart=cart,
#                     )
#                     product.stock -= order_item.quantity  # Deduct the stock from the product
#                     product.save()

#                 cart_items.append(item)

#             CartItem.objects.bulk_create(cart_items)
#             cart = Cart.objects.calculate_price(request.user)
#             calculation = return_cart_summary(
#                 cart.total_price, cart.tax, cart.discount_percentage
#             )
#             serializer = CartSerializer(cart, context={"lang": lang})
#             return Response(
#                 {"item": serializer.data, "order_summary": calculation},
#                 status=HTTP_201_CREATED,
#             )
        
#         except ProductItem.DoesNotExist:
#             return Response(
#                 {"message": "Product item no longer exists"}, status=HTTP_400_BAD_REQUEST
#             )
#         except Product.DoesNotExist:
#             return Response(
#                 {"message": "Product no longer exists"}, status=HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             return Response(
#                 {"message": f"An error occurred while reordering: {str(e)}"}, status=HTTP_400_BAD_REQUEST
#             )


class ReOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # Clear the existing cart items
        CartItem.objects.filter(cart__user=request.user).delete()
        cart, created = Cart.objects.get_or_create(user=request.user)
        lang = get_language_from_request(request)
        order = get_object_or_404(Order, id=pk)
        order_items = OrderItem.objects.filter(order=order)
        cart_items = []

        try:
            for order_item in order_items:
                if order_item.product_item_id:  # Check if there's a specific variant
                    product_item = get_object_or_404(ProductItem, id=order_item.product_item_id)
                    
                    # Check if the stock of the product item is sufficient
                    if product_item.stock < order_item.quantity:
                        return Response(
                            {"message": f"Insufficient stock for {product_item.product.title} - {product_item.variant_name}"},
                            status=HTTP_400_BAD_REQUEST
                        )
                    
                    # Create the cart item for the variant
                    item = CartItem(
                        product=product_item.product,  # Set the main product
                        product_item=product_item,  # Set the variant
                        quantity=order_item.quantity,
                        cart=cart,
                    )
                    cart_items.append(item)

                else:  # Handle products without variants
                    product = get_object_or_404(Product, id=order_item.product_uuid)
                    
                    # Check if the stock of the product is sufficient
                    if product.stock < order_item.quantity:
                        return Response(
                            {"message": f"Insufficient stock for {product.title}"},
                            status=HTTP_400_BAD_REQUEST
                        )
                    
                    # Create the cart item for the product
                    item = CartItem(
                        product=product,
                        quantity=order_item.quantity,
                        cart=cart,
                    )
                    cart_items.append(item)

            # Bulk create the cart items
            CartItem.objects.bulk_create(cart_items)

            # Recalculate cart totals
            cart = Cart.objects.calculate_price(request.user)
            calculation = return_cart_summary(
                cart.total_price, cart.tax, cart.discount_percentage
            )
            serializer = CartSerializer(cart, context={"lang": lang})

            return Response(
                {"item": serializer.data, "order_summary": calculation},
                status=HTTP_201_CREATED,
            )
        
        except ProductItem.DoesNotExist:
            return Response(
                {"message": "Product item no longer exists"}, status=HTTP_400_BAD_REQUEST
            )
        except Product.DoesNotExist:
            return Response(
                {"message": "Product no longer exists"}, status=HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred while reordering: {str(e)}"}, status=HTTP_400_BAD_REQUEST
            )

