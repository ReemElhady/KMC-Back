from django.utils import translation
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import GenericViewSet

from ..models.article_model import Article
from ..serializers.article_serializer import (
    ArticleListSerializer,
    ArticleDetailSerializer,
)


class ArticleAPI(GenericViewSet, ListAPIView, RetrieveAPIView):

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return Article.objects.filter(isArchived=False).translate(lang).order_by("-id")

    def get_serializer_class(self):
        if self.kwargs.get("pk"):
            return ArticleDetailSerializer
        return ArticleListSerializer


# class ArticleListAPI(APIView):
#
#     def get(self, request):
#         lang = translation.get_language_from_request(request)
#         content = Article.objects.all().translate(lang)
#         serializer = ArticleListSerializer(content, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class ArticleDetailAPI(APIView):
#
#     def get(self, request, pk):
#         if Article.objects.get(id=pk):
#             lang = translation.get_language_from_request(request)
#             content = Article.objects.translate(lang).get(id=pk)
#             serializer = ArticleDetailSerializer(content)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(status.HTTP_404_NOT_FOUND)
