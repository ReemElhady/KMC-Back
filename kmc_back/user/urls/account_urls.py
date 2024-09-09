from django.urls import path

from user.views.user_account import UserAccountAPI, ChangePasswordApi

urlpatterns = [
    path("", UserAccountAPI.as_view(), name="account"),
    path("change-password", ChangePasswordApi.as_view(), name="change-password"),
]
