from django.urls import path

from offers.views.offer_view import OfferView

urlpatterns = [
    path("", OfferView.as_view(), name="offers")

]
