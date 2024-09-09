from django.urls import path
from smsa.views import WebhookView, ZoneCitiesAPI

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="smsa_webhook"),
    path("zone-cities/", ZoneCitiesAPI.as_view(), name="zone_cities_api"),
]
