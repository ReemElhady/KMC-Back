from rest_framework.exceptions import NotAcceptable
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

# from user.helpers.user_helpers import sendOtp, calculate_time_diff
# from user.models.otp_models import OTP
from user.models.user_model import User
from user.serializers.user_serializer import CreateUserSerializer
from wasage import Wasage


class UserAccountAPI(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = (TokenAuthentication, )
    serializer_class = CreateUserSerializer

    def get_object(self):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        data = self.request.data
        # otp = get_object_or_404(OTP, user=user)

        if request.method == "PUT":
            user.name = data.get("name", None)
            user.email = data.get("email", None)
            wasage_response = None
            if not user.phone == data.get("phone", None):
                if User.objects.filter(phone=data.get("phone")).count():
                    raise NotAcceptable("This Phone number is already registered")
                # otp.save()
                # sendOtp(otp, data.get('phone'))
                wasage_response = Wasage.send_otp(user.id)
            user.save()
            if wasage_response:
                return Response(wasage_response, status=HTTP_200_OK)

            return Response(status=HTTP_200_OK)
        # elif request.method == 'PATCH':
        #     ## Expire time for local dev
        #     # if not calculate_time_diff(otp.modified) < 7380.0 or otp.code != self.request.data.get(
        #     #         'code'):
        #     # Expire time for server dev
        #     if not calculate_time_diff(otp.modified) < 180.0 or otp.code != data.get(
        #             'code'):
        #         raise NotAcceptable("Code Expired or not correct")
        #
        #     user.phone = data.get('phone', None)
        #     user.save()
        #     return Response(status=HTTP_201_CREATED)


class ChangePasswordApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        if user.check_password(request.data["old_password"]):
            if len(request.data["new_password"]) >= 5:
                if request.data["confirm_password"] == request.data["new_password"]:
                    user.set_password(request.data["new_password"])
                    user.save()
                    return Response(status=HTTP_200_OK)
                else:
                    raise NotAcceptable(
                        "Make sure that confirm password matches the entered new password"
                    )
            else:
                raise NotAcceptable("Password must contain at least 5 characters")
        else:
            raise NotAcceptable("Old Password is incorrect")
