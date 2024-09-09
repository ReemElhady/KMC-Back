from rest_framework import serializers

from courses.models.courses_model import Course
from product.models.product_models import Branch


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            'type',
            'branch',
            "image",
            "title",
            "description",
            "number_of_videos",
            "duration",
            "level",
            "instructor_name",
            "instructor_position",
            "brand",
        ]


class SingleCourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            'type',
            'branch',
            "title",
            "image",
            "language",
            "fees",
            "description",
            "number_of_videos",
            "duration",
            "level",
            "instructor_name",
            "instructor_position",
            "iframe_link",
        ]


class BranchSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
