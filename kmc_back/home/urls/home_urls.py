from django.urls import path

from ..views.home_views import HomeAPIView

urlpatterns = [
    path("", HomeAPIView.as_view(), name="home-view")
]
