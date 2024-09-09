from rest_framework import serializers

from smsa.models import ZoneCity

# from smsa.serializers import ZoneCitySerializer
# from user.helpers.user_address_helpers import COUNTRY_OPTIONS
from user.models.user_address import UserAddress


class UserAddressSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", required=False)

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "name",
            "phone",
            "phone_country_code",
            "country",
            "city",
            "city_name",
            "address",
            "building",
            "floor",
            "apartment",
            "is_default",
        ]
        read_only_fields = ["id", "is_default"]
