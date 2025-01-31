from django.urls import path

from ..views.home_views import HomeAPIView, RotatingAdAPIView, GalleryImageView, DemoBookingAPI, DemoBookingPageAPI

urlpatterns = [
    path("", HomeAPIView.as_view(), name="home-view"),
    path('ad/', RotatingAdAPIView.as_view(), name='ad-api'),
    path('gallery/', GalleryImageView.as_view(), name='gallery-images'),
    path('book-demo-page', DemoBookingPageAPI.as_view(), name='book-demo-page'),
    path('book-demo', DemoBookingAPI.as_view(), name='book-demo'),
    # path('flash-sale/', FlashSaleView.as_view(), name='flash-sale'),
]
