from urllib.parse import urlparse, parse_qs

from django.core import validators
from django.db import models
from django_resized import ResizedImageField
from translations.models import Translatable

from courses.helpers.courses_help import allowed_extensions, extension_error_message, fileSize
from product.models.product_models import Type, Branch, Brand


class Course(Translatable):
    type = models.ForeignKey(Type, related_name="type_courses", on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name="branch_courses", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name="brand_courses", on_delete=models.CASCADE, null=True)
    image = ResizedImageField(upload_to="courses", validators=[
        validators.FileExtensionValidator(allowed_extensions, extension_error_message), fileSize])
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    fees = models.CharField(max_length=255)
    description = models.TextField()
    number_of_videos = models.PositiveBigIntegerField()
    duration = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    instructor_name = models.CharField(max_length=255)
    instructor_position = models.CharField(max_length=255)
    iframe_link = models.CharField(max_length=255, null=True)

    class TranslatableMeta:
        fields = ['title', 'language', 'fees', 'description', 'duration', 'level', 'instructor_name',
                  'instructor_position']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            parsed_url = urlparse(self.iframe_link)
            video_id = parse_qs(parsed_url.query).get('v')
            if video_id:
                video_id = video_id[0]
            else:
                video_id = self.iframe_link.split('/')[-1]
            self.iframe_link = f'https://www.youtube.com/embed/{video_id}'
        except:
            pass
        super().save(*args, **kwargs)
