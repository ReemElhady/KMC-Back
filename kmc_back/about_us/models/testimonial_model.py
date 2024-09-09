from django.db import models
from translations.models import Translatable
from about_us.helpers.about_us_helper import (
    allowed_extensions,
    extension_error_message,
    fileSize,
)
from django_resized import ResizedImageField
from django.core import validators


class Testimonials(Translatable):
    about_us = models.ForeignKey(
        "AboutUs", related_name="about_us_testimonial", on_delete=models.CASCADE
    )
    name= models.CharField(max_length=255, blank= True,null=True)
    
    text= models.CharField(max_length=255, blank= True,null=True)

    image = ResizedImageField(
        upload_to="about_us/testimonials",
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            fileSize,
        ],
        default="",
    )
    class TranslatableMeta:
        fields = ["name", "text"]

    class Meta:
        verbose_name_plural = "About us testimonials"
