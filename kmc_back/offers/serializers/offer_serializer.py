from rest_framework import serializers


class OfferSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    image = serializers.CharField(max_length=255, source="image.url")
