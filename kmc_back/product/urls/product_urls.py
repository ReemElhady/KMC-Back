from django.urls import path
from rest_framework import routers

# from product.models.product_models import Review
from product.views.product_views import (
    TypeListView,
    ProductAPIView,
    ProductDetailsView,
    BranchesAndBrandsView,
    WishListAPIView,
    # BrandListView,
    ProductsByBrandAPIView,
    ProductsByBranchAPIView
)

# router.register("", ProductAPIView),
router = routers.SimpleRouter()

urlpatterns = [
    path("types", TypeListView.as_view()),
    path("details/<uuid:pk>", ProductDetailsView.as_view()),
    path("", ProductAPIView.as_view()),
    # path("review/<uuid:pk>", ReviewAPIView.as_view()),
    path("wishlist", WishListAPIView.as_view()),
    path("wishlist/<uuid:pk>", WishListAPIView.as_view()),
    # path("review", ReviewAPIView.as_view()),
    path("branches-brands/<int:pk>", BranchesAndBrandsView.as_view()),
    # path("brands/<int:pk>", BrandListView.as_view()),
    path('by-brand/<int:brand_id>/', ProductsByBrandAPIView.as_view()),
    path('by-branch/<int:branch_id>/', ProductsByBranchAPIView.as_view()),
]
urlpatterns += router.urls
