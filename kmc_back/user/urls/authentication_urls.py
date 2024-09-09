from django.urls import path

from user.views.authentication_apis import SignUpAPI, ResetForgetPassword, WasageCallBackApiView, CheckIsActiveUserApiView, RegenerateWassageQRCodeApiView

urlpatterns = [
    path('register/', SignUpAPI.as_view(), name='register'),
    # path('resend-otp/', ResendOtpAPI.as_view(), name='resend_otp'),
    path('reset-forget-password/', ResetForgetPassword.as_view(), name='reset_forget_password'),
    path("wasage/", WasageCallBackApiView.as_view(), name="wasage"),
    path("check-user/<str:phone>/", CheckIsActiveUserApiView.as_view(), name="check_is_active_user"),
    path("regenerate-qrcode/", RegenerateWassageQRCodeApiView.as_view(), name="regenerate_qrcode")
]
