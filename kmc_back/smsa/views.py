from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from order.models.order_models import Order
from smsa.serializers import WebhookPayloadSerializer, ZoneCitySerializer
from smsa.models import ZoneCity
from smsa.custom_authentication import CustomAuthentication


class ZoneCitiesAPI(APIView):
    @staticmethod
    def get(request):
        cities = ZoneCity.objects.all()
        serializer = ZoneCitySerializer(cities, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class WebhookView(APIView):
    authentication_classes = [
        CustomAuthentication,
    ]

    @staticmethod
    def post(request):
        data = request.data
        if not data[0].get("AWB"):
            return Response("Bad Request", status=status.HTTP_400_BAD_REQUEST)

        orders_to_update = []
        awbs = []
        scans_dict = {}
        for item in data:
            awbs.append(item["AWB"])
            scans_dict[item["AWB"]] = item.get("Scans")
        orders = Order.objects.filter(awb__in=awbs)
        for order in orders:
            print("BEFORE",order.shipping_status)
            scan = scans_dict[order.awb]
            sorted_scans = sorted(scan, key=lambda x: x["ScanDateTime"], reverse=True)
            last_scan = sorted_scans[0].get("ScanDescription")
            order.shipping_status = last_scan
            orders_to_update.append(order)
            print("AFTER",order.shipping_status)
        Order.objects.bulk_update(orders_to_update, ["shipping_status"])
        return Response("Orders updated successfully", status=status.HTTP_200_OK)
