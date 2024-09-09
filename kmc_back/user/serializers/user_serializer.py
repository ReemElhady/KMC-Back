from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models.user_model import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone"] = user.phone or None
        token["name"] = user.name
        token["id"] = user.id
        token["email"] = user.email
        return token


class CreateUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=5)
    email = serializers.EmailField(allow_null=True, required=False)

    def validate(self, attrs):
        if attrs.get("email"):
            attrs.get("email").lower()
        if len(User.objects.filter(phone=attrs.get("phone"), is_active=True)) > 0:
            raise ValidationError("User with this phone already exists")
        else:
            if not attrs.get("password") == self.context.get("re_password"):
                raise ValidationError(
                    "Please confirm that the re-entered password matches the original password"
                )
            return attrs

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
