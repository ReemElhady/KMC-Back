from rest_framework import serializers

from about_us.models.about_us_model import AboutUs
from about_us.models.about_us_statistics import AboutUsStatistics
from about_us.models.testimonial_model import Testimonials


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonials
        fields = "__all__"


class AboutUsStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsStatistics
        fields = [
            "id",
            "sav",
            "number",
            "text",
        ]


class AboutUsSerializer(serializers.ModelSerializer):
    about_us_testimonial = serializers.SerializerMethodField()
    about_us_statistics = serializers.SerializerMethodField()

    def get_about_us_testimonial(self, obj):
        lang = self.context.get("lang")
        query = Testimonials.objects.translate(lang).all()
        return TestimonialSerializer(query, many=True).data

    def get_about_us_statistics(self, obj):
        lang = self.context.get("lang")
        query = AboutUsStatistics.objects.translate(lang).all()
        return AboutUsStatisticSerializer(query, many=True).data

    class Meta:
        model = AboutUs
        fields = "__all__"
