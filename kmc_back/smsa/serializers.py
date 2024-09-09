from rest_framework import serializers


class WebhookPayloadSerializer(serializers.Serializer):
    awb = serializers.CharField()
    cod_amount = serializers.FloatField()


class ZoneCitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
