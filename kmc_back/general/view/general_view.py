from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from general.models.general_model import General


class GeneralAPI(APIView):
    @permission_classes(AllowAny)
    def get(self, req):
        general = General.objects.all().values().first()
        # user = req.user
        # total_points = 0
        # if not user.is_anonymous:
        #     total_points = get_total_points(user)
        return Response({"general": general, 'total_points': 0}, status=HTTP_200_OK)
