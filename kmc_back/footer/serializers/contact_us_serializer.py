from rest_framework import serializers


class ContactUsSerializer(serializers.Serializer):
    phone = serializers.CharField()
    phone1 = serializers.CharField()
    email = serializers.EmailField()
