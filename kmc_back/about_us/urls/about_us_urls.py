from django.urls import path

from about_us.views.about_us_view import AboutUsView

urlpatterns = [
    path("", AboutUsView.as_view(), name="aboutUs")

]
