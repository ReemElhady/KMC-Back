from django.urls import path

from footer.views.footer_view import FooterAPI

urlpatterns = [
    path("", FooterAPI.as_view()),

]
