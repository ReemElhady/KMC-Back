from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from cart.models import Cart
from coupon.views.coupon_views import apply_coupon
from user.models.user_address import UserAddress
from user.serializers.user_address_serializers import UserAddressSerializer
from smsa.smsa import SMSAIntegration


class CreateUserAddressAPI(ViewSet):
    permission_classes = [
        IsAuthenticated,
    ]

    def addresses_list(self, request):
        user = request.user
        # user = get_user_model().objects.get(id=1)
        addresses_object = UserAddress.objects.filter(user_id=user.id)
        addresses = UserAddressSerializer(addresses_object, many=True).data
        cart = Cart.objects.calculate_price(request.user)

        if not cart:
            return Response("This User has no cart", status=status.HTTP_404_NOT_FOUND)

        discount = 0.0
        if cart.coupon:
            coupon, response_code = apply_coupon(
                cart, cart.cart_items_cart.all(), user, "en", cart.coupon
            )
            discount = coupon["discount_value"]

        for address in addresses:
            shipping_details = SMSAIntegration.calculate_shipping_price(
                cart.total_price,
                discount,
                cart.total_weight,
                address["city"],
            )
            address["shipping_details"] = shipping_details
        return Response(addresses, status=status.HTTP_200_OK)

    def create_address(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            # user = get_user_model().objects.get(id=1)
            userAddress = UserAddress(user=user, **serializer.validated_data)
            addresses_counts = UserAddress.objects.filter(user_id=user.id).count()
            if addresses_counts == 0:
                userAddress.is_default = True
            userAddress.save()
            serializeredData = UserAddressSerializer(userAddress)
            return Response(serializeredData.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_address(self, request, addressId):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = request.user
                # user = get_user_model().objects.get(id=1)
                store_address = UserAddress.objects.get(id=addressId, user_id=user.id)
                store_address.name = serializer.validated_data["name"]
                store_address.phone = serializer.validated_data["phone"]
                store_address.phone_country_code = serializer.validated_data[
                    "phone_country_code"
                ]
                store_address.country = serializer.validated_data["country"]
                store_address.city = serializer.validated_data["city"]
                store_address.address = serializer.validated_data["address"]
                store_address.building = serializer.validated_data["building"]
                store_address.floor = serializer.validated_data["floor"]
                store_address.apartment = serializer.validated_data["apartment"]
                store_address.save()
                serializeredData = UserAddressSerializer(store_address)
                return Response(serializeredData.data, status=status.HTTP_200_OK)
            except UserAddress.DoesNotExist:
                return Response(
                    {"not_exist", "address is not exist ."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except:
                return Response(
                    {"server_error": "something wrong in server , please try later ."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_address(self, request, addressId):
        try:
            user = request.user
            # user = get_user_model().objects.get(id=1)
            store_address = UserAddress.objects.get(id=addressId, user_id=user.id)

            if store_address.is_default:
                store_address.delete()
                last_address = UserAddress.objects.filter(user_id=user.id).last()
                if last_address:
                    last_address.is_default = True
                    last_address.save(update_fields=["is_default"])

            else:
                store_address.delete()

            return Response(
                {"success": "address had deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except UserAddress.DoesNotExist:
            return Response(
                {"not_exist", "address is not exist ."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except:
            return Response(
                {"server_error": "something wrong in server , please try later ."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def mark_address_as_default(self, request, addressId):
        try:
            user = request.user
            # user = get_user_model().objects.get(id=1)
            store_address = UserAddress.objects.get(id=addressId, user_id=user.id)
            addresses = UserAddress.objects.filter(user_id=user.id)
            for address in addresses:
                address.is_default = False
                address.save()
            store_address.is_default = True
            store_address.save()
            serializeredData = UserAddressSerializer(store_address)
            return Response(serializeredData.data, status=status.HTTP_200_OK)
        except UserAddress.DoesNotExist:
            return Response(
                {"not_exist", "address is not exist ."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except:
            return Response(
                {"server_error": "something wrong in server , please try later ."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
