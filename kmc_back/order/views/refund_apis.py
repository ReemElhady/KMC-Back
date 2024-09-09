from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView

from common.tasks import async_send_email
from order.models.order_models import Order, OrderItem
from order.models.refund_models import Refund, RefundItem
from order.serializers.order_serializer import OrderSerializer
from order.utility.order_utility import can_refund

# class RefundAPI(APIView):
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 data = request.data
#                 order = (
#                     Order.objects.filter(id=data.get("id"), user=request.user)
#                     .prefetch_related("order_item")
#                     .first()
#                 )

#                 if order is None:
#                     return Response(
#                         {"message": "Order is invalid"}, status=HTTP_400_BAD_REQUEST
#                     )
#                 if not can_refund(order):
#                     return Response(
#                         {"message": "this order can't be refunded"},
#                         status=HTTP_400_BAD_REQUEST,
#                     )
#                 # order_created_at = order.created_at.replace(tzinfo=None)
#                 # if (datetime.now() - order_created_at).days > 14:
#                 #     return Response({'message': "Can't refund after 14 days of order"}, status=HTTP_400_BAD_REQUEST)

#                 # if Refund.objects.filter(order=order).first():
#                 #     return Response({'message': 'This order has a refund request'}, status=HTTP_400_BAD_REQUEST)
#                 refund, created = Refund.objects.get_or_create(
#                     order=order, reason=request.data.get("reason")
#                 )
#                 refund.save()

#                 refunded_items = []
#                 order_items = []
#                 for item in data.get("refunded_items"):
#                     order_item = get_object_or_404(OrderItem, id=item["id"])
#                     order_item.status = "Refund Requested"
#                     order_items.append(order_item)
#                     if order_item.quantity < item["quantity"]:
#                         return Response(
#                             {
#                                 "message": "Requested quantity is more than ordered quantity"
#                             },
#                             status=HTTP_400_BAD_REQUEST,
#                         )
#                     ref_item = RefundItem(
#                         refund=refund,
#                         order_item=order_item,
#                         requested_quantity=item["quantity"],
#                         reason=item["reason"],
#                     )
#                     refunded_items.append(ref_item)
#                 RefundItem.objects.bulk_create(refunded_items)
#                 OrderItem.objects.bulk_update(order_items, ["status"])

#                 async_send_email(
#                     subject="New Refund Request",
#                     message=f"New refund by {order.user.name} in order ({order.code})",
#                     receivers=[
#                         "mazen@kandilmedical.com",
#                         "ahmed@kandilmedical.com",
#                         "Karim@kandilmedical.com",
#                     ],
#                 )

#                 order.order_status = "Refund requested"
#                 order.save()

#                 order = OrderSerializer(order).data
#             return Response({"order": order}, status=HTTP_201_CREATED)
#         except Exception as exception:
#             return Response({"exception": str(exception)}, status=HTTP_400_BAD_REQUEST)
from order.tasks import async_send_order_email

class RefundAPI(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                order = get_object_or_404(Order, id=data.get("id"), user=request.user)
                
                # Check if the order can be refunded
                if not can_refund(order):
                    return Response({"message": "This order can't be refunded"}, status=HTTP_400_BAD_REQUEST)

                # Update order status
                order.order_status = "Refund Requested"
                order.save()

                # Create Refund and RefundItem records
                refund, created = Refund.objects.get_or_create(order=order, reason=request.data.get("reason"))
                for item in data.get("refunded_items"):
                    order_item = get_object_or_404(OrderItem, id=item["id"])
                    RefundItem.objects.create(
                        refund=refund,
                        order_item=order_item,
                        requested_quantity=item["quantity"],
                        reason=item.get("reason", "")
                    )
                
                
                async_send_order_email.delay(user_id=order.user.id, order_id=order.id)
                
            return Response({"order": order.id}, status=HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
