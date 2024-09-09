from django.utils.translation import get_language_from_request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from about_us.models.about_us_model import AboutUs
from about_us.serializers.about_us_serializer import AboutUsSerializer


class AboutUsView(APIView):
    def get(self, req):
        lang = get_language_from_request(req)
        content = AboutUs.objects.translate(lang).first()
        serializer = AboutUsSerializer(content, context={'lang': lang})
        return Response(serializer.data, status=HTTP_200_OK)
