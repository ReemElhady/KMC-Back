from django.conf import settings
from django.utils import translation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from common.tasks import async_send_email
from ..models.contact_us_model import ContactUs
from ..serializers.contact_us_serializer import (
    ContactUsSerializer,
    ContactFormSerializer,
)


class ContactUsAPI(ViewSet):

    def get_contact_us_content(self, request):
        lang = translation.get_language_from_request(request)
        content = ContactUs.objects.translate(lang).last()
        serializer = ContactUsSerializer(content, context={"lang": lang})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post_form(self, request):
        serializer = ContactFormSerializer(data=request.data)

        message = (
            "Name: "
            + request.data["name"]
            + "\nEmail: "
            + request.data["email"]
            + "\nPhone Number: "
            + request.data["phone"]
            + "\nMessage: "
            + request.data["message"]
        )
        if serializer.is_valid():
            serializer.save()

            async_send_email.delay(
                subject=request.data["subject"],
                message=message,
                receivers=[settings.EMAIL_HOST_USER],
            )

            return Response(
                {"message": "Your message has been sent", "is_error": False},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": serializer.errors, "is_error": True},
                status=status.HTTP_403_FORBIDDEN,
            )
