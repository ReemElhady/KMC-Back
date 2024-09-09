from django.db.models import Prefetch
from django.utils import translation
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from product.filters.product_filters import ProductFilter
from product.models.product_models import (
    Type,
    Product,
    WishList,
    Branch,
    Brand,
    SubBranch,
)
from product.serializer.product_serializers import (
    TypeSerializer,
    ProductDetailsSerializer,
    ProductListSerializer,
    BranchSerializer,
    BrandSerializer,
    WishListSerializer,
)


class TypeListView(ListAPIView):
    serializer_class = TypeSerializer
    pagination_class = None

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return Type.objects.all().order_by("display_ordering").translate(lang)


class ProductAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    @permission_classes(AllowAny)
    def get_serializer_context(self):
        context = super(ProductAPIView, self).get_serializer_context()
        user = self.request.user
        context.update({"user": user})
        return context

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return (
            Product.objects.filter(is_archived=False, weight__gt=0)
            .translate_related("product_item")
            .translate(lang)
            .prefetch_related("product_image", "product_url", "product_wishlist")
            .order_by("id")
        )

    # def get(self, request, pk):
    #     lang = translation.get_language_from_request(request)
    #     user = request.user
    #     context = {'user': user, 'lang': lang}
    #     product_query = Product.objects.filter(type_id=pk, is_archived=False).translate(
    #         lang).prefetch_related(
    #         'product_image', 'product_url', 'product_wishlist')
    #     product_serializer = ProductListSerializer(product_query, many=True, context=context).data
    #     branch_query = Branch.objects.filter(type_id=pk).translate(lang)
    #     branch_serializer = BranchSerializer(branch_query, many=True, context=context).data
    #     return Response({'products': product_serializer, 'branches': branch_serializer})


class BranchesAndBrandsView(APIView):
    def get(self, request, pk):
        lang = translation.get_language_from_request(request)
        brand_query = (
            Brand.objects.filter(product_brand__type__id=pk).distinct().translate(lang)
        )
        brand_serializer = BrandSerializer(brand_query, many=True).data
        branch_query = (
            Branch.objects.filter(product_branch__type__id=pk)
            .prefetch_related(
                Prefetch(
                    "branch_sub_branches",
                    queryset=SubBranch.objects.filter(
                        product_sub_branch__type__id=pk
                    ).distinct(),
                )
            )
            .translate_related("branch_sub_branches")
            .distinct()
            .translate(lang)
        )
        branch_serializer = BranchSerializer(branch_query, many=True).data
        return Response({"brands": brand_serializer, "branches": branch_serializer})


class ProductDetailsView(RetrieveAPIView):
    serializer_class = ProductDetailsSerializer

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return (
            Product.objects.filter(is_archived=False, weight__gt=0)
            .translate_related("product_item")
            .translate(lang)
            .prefetch_related(
                "product_image",
                "product_url",
                "product_wishlist",
            )
        )

    @permission_classes(AllowAny)
    def get_serializer_context(self):
        context = super(ProductDetailsView, self).get_serializer_context()
        lang = translation.get_language_from_request(self.request)
        user = self.request.user
        context.update({"lang": lang, "user": user})
        return context


# class ReviewAPIView(APIView, LimitOffsetPagination):
#     # permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         query = Review.objects.filter(product=self.kwargs.get('pk'))
#         query = self.paginate_queryset(query, request)
#         serializer = ReviewSerializer(query, many=True).data
#         return self.get_paginated_response(serializer)
#
#     @permission_classes(IsAuthenticated)
#     def post(self, request, *args, **kwargs):
#         try:
#             request.data['user'] = request.user
#             review = Review.objects.create(**request.data)
#             serializer = ReviewSerializer(review)
#             return Response({'review': serializer.data, 'product_rate': review.product.rate}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     @permission_classes(IsAuthenticated)
#     def delete(self, request, *args, **kwargs):
#         try:
#             product = get_object_or_404(Product, id=self.kwargs.get('pk'))
#             query = Review.objects.filter(product=product, user=request.user)
#             if query.exists():
#                 query.delete()
#                 return Response({'product_rate': product.rate}, status=status.HTTP_200_OK)
#             return Response({"Review doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#


class WishListAPIView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = (
            WishList.objects.filter(user=self.request.user)
            .select_related("product")
            .order_by("id")
        )
        query = self.paginate_queryset(query, request)
        serializer = WishListSerializer(query, many=True).data
        return self.get_paginated_response(serializer)

    def post(self, request, *args, **kwargs):
        try:
            wishlist = WishList.objects.create(
                user=request.user, product_id=request.data.get("pk")
            )
            serializer = WishListSerializer(wishlist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            WishList.objects.filter(
                user=request.user, product_id=self.kwargs.get("pk")
            ).delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
