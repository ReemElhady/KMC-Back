from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from user.views.authentication_apis import MyTokenObtainPairView
from .settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/contact-us/", include("contact_us.urls.contact_us_url")),
        path("api/about-us/", include("about_us.urls.about_us_urls")),
        path("api/user/address/", include("user.urls.user_address_urls")),
        path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
        path(
            "api/token/refresh/",
            jwt_views.TokenRefreshView.as_view(),
            name="token_refresh",
        ),
        path("api/user/auth/", include("user.urls.authentication_urls")),
        path("api/user/account/", include("user.urls.account_urls")),
        path("api/product/", include("product.urls.product_urls")),
        path("api/courses/", include("courses.urls.courses_urls")),
        path("api/article/", include("article.urls.article_urls")),
        path("api/points/", include("points.urls.points_urls")),
        path("api/cart/", include("cart.urls.cart_urls")),
        path("api/coupon/", include("coupon.urls.coupon_urls")),
        path("api/article/", include("article.urls.article_urls")),
        path("api/order/", include("order.urls.order_urls")),
        path("api/general/", include("general.urls.general_urls")),
        path("api/home/", include("home.urls.home_urls")),
        path("api/offers/", include("offers.urls.offer_urls")),
        path("api/footer/", include("footer.urls.footer_urls")),
        path("api/faq/", include("FAQ.urls.FAQ_urls")),
        path("api/smsa/", include("smsa.urls")),
        # path("sentry-debug/", trigger_error),
    ]
    + static(MEDIA_URL, document_root=MEDIA_ROOT)
    + static(STATIC_URL, document_root=STATIC_ROOT)
)


admin.site.site_header = "KMC Admin Panel"
admin.site.index_title = "KMC Admin Panel"
