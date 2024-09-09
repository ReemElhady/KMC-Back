from django.utils.translation import get_language_from_request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from offers.models.offer_model import Offer
from offers.serializers.offer_serializer import OfferSerializer


class OfferView(APIView):
    def get(self, req):
        lang = get_language_from_request(req)
        content = Offer.objects.translate(lang).first()
        serializer = OfferSerializer(content)
        return Response(serializer.data, status=HTTP_200_OK)
