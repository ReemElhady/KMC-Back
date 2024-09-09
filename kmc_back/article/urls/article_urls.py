from django.conf.urls.static import static
from rest_framework import routers

from kmc_back import settings
from ..views.article_view import ArticleAPI

router = routers.SimpleRouter()
router.register("", ArticleAPI, basename='Article')

urlpatterns = [
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_ROOT)

urlpatterns += router.urls
