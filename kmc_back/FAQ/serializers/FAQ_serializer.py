from rest_framework import serializers


class FAQSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()
