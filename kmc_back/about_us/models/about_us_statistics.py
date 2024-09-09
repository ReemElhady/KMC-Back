from django.core import validators
from django.db import models
from translations.models import Translatable

from about_us.helpers.about_us_helper import allowed_extensions, extension_error_message, fileSize


class AboutUsStatistics(Translatable):
    about_us = models.ForeignKey('AboutUs', related_name="about_us_statistics", on_delete=models.CASCADE)
    sav = models.FileField(upload_to="about_us/statistic",
                           validators=[
                               validators.FileExtensionValidator(allowed_extensions, extension_error_message),
                               fileSize
                           ]
                           )
    number = models.IntegerField()
    text = models.CharField(max_length=255)

    class TranslatableMeta:
        fields = ["text", "number"]

    def __str__(self):
        return f"{self.text} - {self.number}"

    class Meta:
        verbose_name_plural = "About us statistics"
