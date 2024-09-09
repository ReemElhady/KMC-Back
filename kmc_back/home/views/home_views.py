from django.utils import translation
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from article.models.article_model import Article
from article.serializers.article_serializer import ArticleListSerializer
from coupon.models import Coupon
from product.serializer.product_serializers import PopularProductSerializer
from ..models import PopularProduct
from ..models.home_models import HomeSwiper, HomeDetails
from ..serializers.home_serializers import SwiperSerializer, HomeDetailsSerializer


class HomeAPIView(APIView):

    @permission_classes(AllowAny)
    def get(self, request):
        lang = translation.get_language_from_request(request)
        swiper_content = HomeSwiper.objects.all()
        swiper_serializer = SwiperSerializer(swiper_content, many=True)

        articles_content = Article.objects.translate(lang).filter(isArchived=False)[::-1][:3]
        article_serializer = ArticleListSerializer(articles_content, many=True)

        top_products_qs = PopularProduct.objects.all()
        top_products = PopularProductSerializer(top_products_qs, many=True, read_only=True,
                                                context={'lang': lang, 'user': request.user}).data
        top_products = list(map(lambda x: x['product'], top_products))

        home_details_content = HomeDetails.objects.all().first()
        home_details_serializer = HomeDetailsSerializer(home_details_content).data
        home_coupon = Coupon.objects.filter(is_home=True).values('code', 'discount_percentage').first()

        return Response({'Home_Swiper': swiper_serializer.data,
                         'Popular_Products': top_products,
                         'Latest_Articles': article_serializer.data,
                         'home_coupon': home_coupon,
                         'home_details': home_details_serializer,
                         }, status=status.HTTP_200_OK)
