from rest_framework import serializers


class ServiceSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    title = serializers.CharField()
    description = serializers.CharField()

