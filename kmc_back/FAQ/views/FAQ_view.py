from django.utils import translation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from FAQ.models.FAQ_model import FAQ
from FAQ.serializers.FAQ_serializer import FAQSerializer


class FaqAPI(APIView):

    def get(self, request):
        lang = translation.get_language_from_request(request)

        faq = FAQ.objects.all().translate(lang)
        faq_serializer = FAQSerializer(faq, many=True)

        return Response(faq_serializer.data, status=status.HTTP_200_OK)
