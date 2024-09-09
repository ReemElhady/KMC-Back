from about_us.models.about_us_model import AboutUs
from about_us.models.about_us_statistics import AboutUsStatistics
from about_us.models.testimonial_model import Testimonials
from kmc_back.generic_admin import *


class TestimonialInline(TranslatableInline):
    model = Testimonials
    extra = 1

    inlines = [TranslationInline]


class AboutAusStatiscisInline(TranslatableInline):
    model = AboutUsStatistics
    extra = 1

    inlines = [TranslationInline]


class AboutUsAdmin(TranslatableAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not AboutUs.objects.exists()

    inlines = [TranslationInline, TestimonialInline, AboutAusStatiscisInline]


class TestimonialAdmin(TranslatableAdmin):
    inlines = [TranslationInline]


class AboutUsStatisticsAdmin(TranslatableAdmin):
    inlines = [TranslationInline]


admin.site.register(AboutUs, AboutUsAdmin)

admin.site.register(Testimonials, TestimonialAdmin)

admin.site.register(AboutUsStatistics, AboutUsStatisticsAdmin)
