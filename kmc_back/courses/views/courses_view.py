from django.utils import translation
from rest_framework.generics import ListAPIView, RetrieveAPIView

from courses.models.courses_model import Course
from courses.serializers.courses_serializers import (
    CourseListSerializer,
    SingleCourseListSerializer,
    BranchSerilaizer,
)
from product.models.product_models import Branch, Brand, Type
from product.serializer.product_serializers import BrandSerializer
from product.serializer.product_serializers import TypeSerializer


class CourseSListView(ListAPIView):
    serializer_class = CourseListSerializer
    pagination_class = None

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return Course.objects.all().translate(lang)


class SingleCourseView(RetrieveAPIView):
    serializer_class = SingleCourseListSerializer

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return Course.objects.translate(lang).all()


class BranchSListView(ListAPIView):
    serializer_class = BranchSerilaizer
    pagination_class = None

    def get_queryset(self):
        lang = translation.get_language_from_request(self.request)
        return Branch.objects.filter(type_id=self.kwargs["type_id"]).translate(lang)


class BrandListView(ListAPIView):
    serializer_class = BrandSerializer
    pagination_class = None
    queryset = Brand.objects.filter(brand_courses__isnull=False)
