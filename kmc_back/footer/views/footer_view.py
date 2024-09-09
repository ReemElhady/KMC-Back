from django.utils import translation

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from contact_us.models.contact_us_model import ContactUs
from footer.models.service_model import Service
from footer.serializers.contact_us_serializer import ContactUsSerializer
from footer.serializers.service_serializer import ServiceSerializer


class FooterAPI(APIView):

    def get(self, request):
        lang = translation.get_language_from_request(request)

        contact_us = ContactUs.objects.translate(lang).last()
        contact_us_serializer = ContactUsSerializer(contact_us)

        services = Service.objects.all().translate(lang)
        service_serializer = ServiceSerializer(services, many=True)

        return Response({
            'contact_us': contact_us_serializer.data,
            'service': service_serializer.data
        }, status=status.HTTP_200_OK)
