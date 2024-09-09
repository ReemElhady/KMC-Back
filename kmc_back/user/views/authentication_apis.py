from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAcceptable
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# from user.helpers.user_helpers import calculate_time_diff
# from user.models.otp_models import OTP
from user.models.user_model import User
from user.serializers.user_serializer import (
    MyTokenObtainPairSerializer,
    CreateUserSerializer,
)
from wasage.wasage import Wasage


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = []
    authentication_classes = []
    serializer_class = MyTokenObtainPairSerializer


class SignUpAPI(CreateAPIView, UpdateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        user = CreateUserSerializer(response.get("user")).data
        wasage_response = response.get("wasage_response")
        response = {
            "user": user,
            "wasage_response": wasage_response,
        }
        return Response(response, status=HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"re_password": self.request.data.get("re_password")})
        return context

    def get_object(self):
        if self.request.method == "PUT":
            return User.objects.get(phone=self.request.data.get("phone"))

    # def update(self, request, *args, **kwargs):
    #     user = self.get_object()
    #     # otp = get_object_or_404(OTP, user=user)
    #
    #     # print("saved code", otp.code)
    #     # print("sent code", self.request.data.get("code"))
    #     # print("time diff", calculate_time_diff(otp.modified))
    #     # print("time_created", otp.created)
    #
    #     # Expire time for server development
    #     if not calculate_time_diff(
    #             otp.modified
    #     ) < 180.0 or otp.code != self.request.data.get("code"):
    #         raise NotAcceptable("Code Expired or not correct")
    #     elif user.is_active is False:
    #         user.is_active = True
    #         user.save()
    #         return Response(status=HTTP_201_CREATED)
    #     else:
    #         return Response(status=HTTP_200_OK)


# class ResendOtpAPI(APIView):
#     permission_classes = []
#     authentication_classes = ()

# def get(self, request):
#     """Monitor Errors in Twilio OTP send"""
#     return Response(status=HTTP_201_CREATED)

# def put(self, request):
#     """Resend OTP"""
#     user = get_object_or_404(User, phone=request.data["phone"])
#     otp = get_object_or_404(OTP, user=user)
#     otp.save()
#     sendOtp(otp, user.phone)
#     return Response(status=HTTP_200_OK)


class ResetForgetPassword(APIView):
    permission_classes = []
    authentication_classes = ()

    def post(self, request):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from user.helpers.user_helpers import send_reset_password_sms

        phone = request.data.get("phone", None)
        user = User.objects.filter(phone=phone)
        if not user:
            raise NotAcceptable("Phone Number does not exist, please signup")
        encrypted_id = urlsafe_base64_encode(
            force_bytes(str(user.first().id) + "&&&" + user.first().name)
        )
        send_reset_password_sms(user, encrypted_id)
        return Response(status=HTTP_202_ACCEPTED)

    def put(self, request):
        from django.utils.http import urlsafe_base64_decode

        try:
            encrypted_id = request.data.get("encrypted_id", None)
            if encrypted_id:
                decrypted_id = urlsafe_base64_decode(str(encrypted_id)).decode("UTF-8")
                id, name = decrypted_id.split("&&&")
                user = get_object_or_404(User, id=int(id))
                new_password = request.data.get("new_password", None)
                confirm_password = request.data.get("confirm_password", None)
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    return Response(status=HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": e}, status=HTTP_400_BAD_REQUEST)


class WasageCallBackApiView(APIView):
    permission_classes = []
    authentication_classes = ()

    def post(self, request):
        otp = request.GET.get("OTP")
        mobile = request.GET.get("Mobile")
        reference = request.GET.get("Reference")
        secret = request.GET.get("Secret")
        client_id = request.GET.get("ClientID")
        client_name = request.GET.get("ClientName")

        response_data = {
            "otp": otp,
            "mobile": mobile,
            "reference": reference,
            "secret": secret,
            "client_id": client_id,
            "client_name": client_name,
        }

        # Validate and correct the phone number
        if mobile.startswith("201"):
            corrected_mobile = "01" + mobile[3:]
        elif mobile.startswith("01"):
            corrected_mobile = mobile
        else:
            return Response(
                {
                    "error": "Invalid phone number, phone number must be started with '01'"
                },
                status=HTTP_400_BAD_REQUEST,
            )
        if secret != Wasage.secret:
            return Response(
                {"error": "Secret is not the same"}, status=HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, phone=corrected_mobile)
        if user:
            user.is_active = True
            user.save()
            return Response(response_data, status=HTTP_201_CREATED)

        return Response(response_data, status=HTTP_200_OK)


class CheckIsActiveUserApiView(APIView):
    permission_classes = []
    authentication_classes = ()

    def get(self, request, phone):
        user = get_object_or_404(User, phone=phone)
        token = MyTokenObtainPairSerializer.get_token(user)

        if user.is_active:
            return Response(
                {"is_active": True, "token": str(token)}, status=HTTP_200_OK
            )
        else:
            return Response(
                {"is_active": False, "token": str(token)}, status=HTTP_404_NOT_FOUND
            )


class RegenerateWassageQRCodeApiView(APIView):
    permission_classes = []
    authentication_classes = ()

    def get(self, request):
        response = Wasage.send_otp("test_user_id")
        return Response(response, status=HTTP_200_OK)
