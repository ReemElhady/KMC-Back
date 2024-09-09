from rest_framework import serializers

from ..models.contact_form_model import ContactForm
from ..models.contact_us_model import ContactUs


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'

    def validate(self, attrs):
        if attrs.get('email'):
            attrs['email'] = attrs.get('email').lower()
        return attrs


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = '__all__'

    def validate(self, attrs):
        if attrs.get('email'):
            attrs.get('email').lower()
        return attrs
