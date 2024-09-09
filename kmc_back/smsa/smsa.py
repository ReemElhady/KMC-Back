import json
import math
from decimal import Decimal
from decimal import ROUND_HALF_UP

import requests
from django.shortcuts import get_object_or_404

from smsa.models import ZoneCity, ShippingFees


class SMSAIntegration:
    production_api = "https://ecomapis.smsaexpress.com"
    sandbox_api = "https://ecomapis-sandbox.azurewebsites.net"
    production_apikey = "521d8e16d1694173ae1b6e765c9c55a1"
    test_apikey = "1ca3c142701d4e05b8c7a2ffe9ddd7ed"
    kmc_address = {
        "ContactName": "kandil medical company",
        "ContactPhoneNumber": "+201092586388",
        "Country": "EG",
        "District": "misr el gdeda",
        "PostalCode": "11757",
        "City": "Cairo",
        "AddressLine1": "8 mohamed youssef el kady st -marghany st -helioplis",
        "AddressLine2": "33 mohamed tawfik diab-makram ebid-nasr city",
    }

    @classmethod
    def create_shipment(
        cls,
        order,
    ):
        cod_amount = 0
        if order.payment_type == "Cash On Delivery":
            cod_amount = order.price_paid
        order_code = order.code
        order_date = order.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        order_weight = order.order_weight
        declared_value = order.total_price
        duty_paid = False
        boxes_num = 1
        # boxes_num = int(order.number_of_boxes)
        order_content_description = "Shipment Description and content"
        shipment_currency = "EGP"
        smsa_retail_id = "0"
        waybill_type = "PDF"
        weight_unit = "KG"
        vat_paid = True

        headers = {
            "apikey": cls.production_apikey,
            "Content-Type": "application/json",
        }

        shipper_address = cls.kmc_address

        address_line2 = f"Country: {order.order_address.country}, City: {order.order_address.city}, Building: {order.order_address.building}, Apartment: {order.order_address.apartment}, Floor: {order.order_address.floor}"
        consignee_address = {
            "ContactName": order.user.name,
            "ContactPhoneNumber": order.order_address.phone,
            "ContactPhoneNumber2": "96600000",
            # "Coordinates": "21.589886,39.1662759",
            "Country": "EG",
            # "District": order.order_address.city,
            # "PostalCode": "",
            "City": order.order_address.city,
            "AddressLine1": order.order_address.address,
            "AddressLine2": address_line2,
            "ConsigneeID": str(order.user.id),
        }

        body = {
            "ConsigneeAddress": consignee_address,
            "ShipperAddress": shipper_address,
            "OrderNumber": order_code,
            "DeclaredValue": declared_value,
            "CODAmount": cod_amount,
            "Parcels": boxes_num,
            "ShipDate": order_date,
            "ShipmentCurrency": shipment_currency,
            "SMSARetailID": smsa_retail_id,
            "WaybillType": waybill_type,
            "Weight": order_weight,
            "WeightUnit": weight_unit,
            "ContentDescription": order_content_description,
            "VatPaid": vat_paid,
            "DutyPaid": duty_paid,
        }

        api = cls.production_api + "/api/shipment/b2c/new"

        response = requests.post(api, data=json.dumps(body), headers=headers)

        if response.json().get("errors"):
            raise Exception("SMSA API Failed")
        return response.json()["sawb"]

    @classmethod
    def query_shipping_status(cls, awb):
        headers = {
            "apikey": cls.production_apikey,
            "Content-Type": "application/json",
        }

        api = cls.production_api + f"/api/shipment/b2c/query/{awb}"
        response = requests.post(api, headers=headers)
        return response.json()

    @staticmethod
    def calculate_shipping_price(total_price, discount, weight, city):
        total_price = Decimal(total_price - discount)
        weight = Decimal(weight)
        # Get shipping zone
        zone_city = get_object_or_404(ZoneCity, id=city)
        zone = zone_city.zone
        # Calculate weight cost
        if weight > 1:
            shipping_cost = zone.first_1_kg_price + (
                zone.additional_1_kg_price * math.ceil(weight - 1)
            )
        else:
            shipping_cost = zone.first_1_kg_price

        # Shipping fess Additional fees and taxes 
        # shipping_cost += shipping_cost * Decimal(0.12)
        # shipping_cost += shipping_cost * Decimal(0.10)
        # shipping_cost += shipping_cost * Decimal(0.14)
        # shipping_cost = shipping_cost.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)
        
        # Retrieve dynamic fees from the database
        fees, created = ShippingFees.objects.get_or_create(
            id=1,  # Assuming you want to always use the first entry
            defaults={
                'fuel_fee_percentage': Decimal(12.00),
                'postal_agency_fee_percentage': Decimal(10.00),
                'vat_percentage': Decimal(14.00),
                'government_fee_percentage': Decimal(10.00),
            }
        )
        # Shipping fees Additional fees and taxes
        shipping_cost += shipping_cost * (fees.fuel_fee_percentage / Decimal(100))
        shipping_cost += shipping_cost * (fees.postal_agency_fee_percentage / Decimal(100))
        shipping_cost += shipping_cost * (fees.vat_percentage / Decimal(100))
        shipping_cost = shipping_cost.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)


        # Calculate COD cost
        if total_price > zone.cod_limit:
            cod_cost = zone.cod_above_cod_limit * (total_price + shipping_cost)
        else:
            cod_cost = zone.cod_up_to_cod_limit

        # COD Additional fees and taxes
        # cod_cost += cod_cost * Decimal(0.10)
        # cod_cost += cod_cost * Decimal(0.14)
        # cod_cost = cod_cost.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)
        
        # COD Additional fees and taxes
        cod_cost += cod_cost * (fees.government_fee_percentage / Decimal(100))
        cod_cost += cod_cost * (fees.vat_percentage / Decimal(100))
        cod_cost = cod_cost.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP)

        shipping_details = {
            "shipping_cost": shipping_cost,
            "cod_cost": cod_cost,
        }

        return shipping_details

    @classmethod
    def return_shipment(
        cls,
        refunded_items,
    ):
        """
        Creates a new Business-to-Customer (B2C) shipment based on a returned order.
        """
        shipment_weight = 0
        declared_value = 0
        for item in refunded_items:
            declared_value += item.order_item.price * item.to_refund_quantity
            shipment_weight += (
                item.order_item.product_item_weight * item.to_refund_quantity
            )
        order = refunded_items[0].order_item.order
        refunded_item_created_at = refunded_items[
            0
        ].order_item.order.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        order_code = order.code
        boxes_num = 1
        order_content_description = "Shipment Description and content"
        shipment_currency = "EGP"
        waybill_type = "PDF"
        weight_unit = "KG"

        headers = {
            "apikey": cls.production_apikey,
            "Content-Type": "application/json",
        }

        return_to_address = cls.kmc_address

        address_line2 = f"Country: {order.order_address.country}, City: {order.order_address.city}, Building: {order.order_address.building}, Apartment: {order.order_address.apartment}, Floor: {order.order_address.floor}"
        pickup_address = {
            "ContactName": order.user.name,
            "ContactPhoneNumber": order.order_address.phone,
            "ContactPhoneNumber2": "96600000",
            "Country": "EG",
            "City": order.order_address.city,
            "AddressLine1": order.order_address.address,
            "AddressLine2": address_line2,
            "ConsigneeID": str(order.user.id),
        }

        body = {
            "PickupAddress": pickup_address,
            "ReturnToAddress": return_to_address,
            "OrderNumber": order_code,
            "DeclaredValue": declared_value,
            "Parcels": boxes_num,
            "ShipDate": refunded_item_created_at,
            "ShipmentCurrency": shipment_currency,
            "WaybillType": waybill_type,
            "Weight": shipment_weight,
            "WeightUnit": weight_unit,
            "ContentDescription": order_content_description,
        }

        api = cls.production_api + "/api/c2b/new"
        response = requests.post(api, data=json.dumps(body), headers=headers)

        return response
