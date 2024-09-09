from django.urls import path

from general.view.general_view import GeneralAPI

urlpatterns = [
    path("", GeneralAPI.as_view()),

]
