from points.views.points_view import PointsAPIView
from django.urls import path

urlpatterns = [
    path("", PointsAPIView.as_view()),
]
