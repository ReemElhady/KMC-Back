from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from courses.models.courses_model import Course


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class CourseAdmin(TranslatableAdmin):
    list_display = (
        "type",
        "branch",
        "title",
        "language",
        "description",
        "number_of_videos",
        "duration",
        "level",
        "instructor_name",
    )
    list_filter = (

        ("type__name", custom_titled_filter("type name")),
        ("branch__name", custom_titled_filter("branch name")),
        "title",
        "language",
        "description",
        "number_of_videos",
        "duration",
        "level",
        "instructor_name",
    )
    search_fields = ['type__name', 'branch__name', 'title', 'description']

    ordering = ["-id"]
    inlines = [TranslationInline]


admin.site.register(Course, CourseAdmin)
