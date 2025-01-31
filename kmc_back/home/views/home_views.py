from django.conf import settings
from django.utils import translation
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from common.tasks import async_send_email
from rest_framework.viewsets import ViewSet

from article.models.article_model import Article
from article.serializers.article_serializer import ArticleListSerializer
from coupon.models import Coupon
from product.models.product_models import Brand, Branch
from product.serializer.product_serializers import PopularProductSerializer, LowInStockProductSerializer, BrandSerializer, BranchSerializer
from ..models import PopularProduct, LowStockProduct
from ..models.home_models import HomeSwiper, HomeDetails, Ad, FlashSale, GalleryImage, DemoBooking, DemoBookingPage
from ..serializers.home_serializers import SwiperSerializer, HomeDetailsSerializer, GalleryImageSerializer, FlashSaleSerializer, DemoBookingSerializer, DemoBookingPageSerializer
from django.http import JsonResponse
from django.utils.timezone import now

class HomeAPIView(APIView):

    @permission_classes(AllowAny)
    def get(self, request):
        lang = translation.get_language_from_request(request)
        
        # Retrieve and order swiper items by position
        swiper_content = HomeSwiper.objects.all().order_by('position')
        swiper_serializer = SwiperSerializer(swiper_content, many=True)

        articles_content = Article.objects.translate(lang).filter(isArchived=False)[::-1][:3]
        article_serializer = ArticleListSerializer(articles_content, many=True)

        top_products_qs = PopularProduct.objects.all()
        top_products = PopularProductSerializer(top_products_qs, many=True, read_only=True,
                                                context={'lang': lang, 'user': request.user}).data
        top_products = list(map(lambda x: x['product'], top_products))

        # Retrieve low stock products
        low_stock_products_qs = LowStockProduct.objects.all()
        low_stock_products = LowInStockProductSerializer(low_stock_products_qs, many=True, read_only=True,
                                                context={'lang': lang, 'user': request.user}).data
        low_stock_products = list(map(lambda x: x['product'], low_stock_products))
        
        home_details_content = HomeDetails.objects.all().first()
        home_details_serializer = HomeDetailsSerializer(home_details_content).data
        home_coupon = Coupon.objects.filter(is_home=True).values('code', 'discount_percentage').first()

        # Retrieve active flash sale
        flash_sale = FlashSale.objects.filter(is_active=True).first()
        flash_sale_data = None
        if flash_sale:
            flash_sale_data = {
                'title': flash_sale.title,
                'start_date': flash_sale.start_date,
                'end_date': flash_sale.end_date,
            }
         # Fetch and serialize all brands
        brands_qs = Brand.objects.all()
        brands = BrandSerializer(brands_qs, many=True).data

        branches_qs=Branch.objects.all()
        branches = BranchSerializer(branches_qs, many=True).data
        
        

        return Response({'Home_Swiper': swiper_serializer.data,
                         'Popular_Products': top_products,
                         'Latest_Articles': article_serializer.data,
                         'home_coupon': home_coupon,
                         'home_details': home_details_serializer,
                         'flash_sale': flash_sale_data,
                         "Low_Stock_Products": low_stock_products,
                         'Brands': brands,
                         'Branches': branches,
                         }, status=status.HTTP_200_OK)



class RotatingAdAPIView(APIView):
    def get(self, request):
        ads = Ad.objects.values_list('text', flat=True)
        if ads:
             return JsonResponse(list(ads), safe=False)



class GalleryImageView(APIView):
    def get(self, request):
        images = GalleryImage.objects.all().order_by('-created_at')
        serializer = GalleryImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class DemoBookingView(APIView):
#     def post(self, request):
#         serializer = DemoBookingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # Send email notification (optional)
#             # You can use Django's EmailMessage or send_mail here
#             return Response({"message": "Booking submitted successfully!"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemoBookingPageAPI(APIView):
    def get(self, request):
        content = DemoBookingPage.objects.last()
        if not content:
            return Response(
                {"message": "No content available."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DemoBookingPageSerializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DemoBookingAPI(APIView):
    def post(self, request):
        serializer = DemoBookingSerializer(data=request.data)

        message = (
            "Name: "
            + request.data["full_name"]
            + "\nEmail: "
            + request.data["email"]
            + "\nPhone Number: "
            + request.data["phone"]
            + "\Device Name: "
            + request.data["device_name"]
            +"\Date: "
            + request.data["date"]
            +"\Time: "
            + request.data["time"]
        )
        if serializer.is_valid():
            serializer.save()

            async_send_email.delay(
                subject=request.data["device_name"],
                message=message,
                receivers=[settings.EMAIL_HOST_USER],
            )

            return Response(
                {"message": "Your message has been sent", "is_error": False},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": serializer.errors, "is_error": True},
                status=status.HTTP_403_FORBIDDEN,
            )
# class FlashSaleView(APIView):
#     def get(self, request):
#         flash_sale = FlashSale.objects.filter(is_active=True, start_date__lte=now(), end_date__gte=now()).first()
#         if flash_sale:
#             serializer = FlashSaleSerializer(flash_sale)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response({'message': 'No active flash sale'}, status=status.HTTP_404_NOT_FOUND)


# class HomeAPIView(APIView):

#     @permission_classes(AllowAny)
#     def get(self, request):
#         lang = translation.get_language_from_request(request)
#         swiper_content = HomeSwiper.objects.all()
#         swiper_serializer = SwiperSerializer(swiper_content, many=True)

#         articles_content = Article.objects.translate(lang).filter(isArchived=False)[::-1][:3]
#         article_serializer = ArticleListSerializer(articles_content, many=True)

#         top_products_qs = PopularProduct.objects.all()
#         top_products = PopularProductSerializer(top_products_qs, many=True, read_only=True,
#                                                 context={'lang': lang, 'user': request.user}).data
#         top_products = list(map(lambda x: x['product'], top_products))

#         home_details_content = HomeDetails.objects.all().first()
#         home_details_serializer = HomeDetailsSerializer(home_details_content).data
#         home_coupon = Coupon.objects.filter(is_home=True).values('code', 'discount_percentage').first()

#         return Response({'Home_Swiper': swiper_serializer.data,
#                          'Popular_Products': top_products,
#                          'Latest_Articles': article_serializer.data,
#                          'home_coupon': home_coupon,
#                          'home_details': home_details_serializer,
#                          }, status=status.HTTP_200_OK)
