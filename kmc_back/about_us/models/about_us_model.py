from django.db import models
from django.core import validators
from django_resized import ResizedImageField
from translations.models import Translatable
from about_us.helpers.about_us_helper import allowed_extensions, extension_error_message, fileSize


class AboutUs(Translatable):
    about_title = models.CharField(max_length=255)
    about_text = models.TextField()
    about_image = ResizedImageField(upload_to="about_us/about",
                                    validators=[
                                        validators.FileExtensionValidator(allowed_extensions, extension_error_message),
                                        fileSize
                                    ]
                                    )
    testimonial_title = models.CharField(max_length=255)
    testimonial_subtitle = models.TextField()
    testimonial_image = ResizedImageField(upload_to="about_us/testimonial",
                                          validators=[
                                              validators.FileExtensionValidator(allowed_extensions,
                                                                                extension_error_message),
                                              fileSize
                                          ]
                                          )

    class TranslatableMeta:
        fields = ["about_title", "about_text", "testimonial_title", "testimonial_subtitle"]

    def __str__(self):
        return self.about_title

    class Meta:
        verbose_name_plural = "About us"
