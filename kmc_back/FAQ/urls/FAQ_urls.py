from django.urls import path

from FAQ.views.FAQ_view import FaqAPI

urlpatterns = [
    path("", FaqAPI.as_view()),

]
