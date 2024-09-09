from django.core import validators
from django.db import models
from django_resized import ResizedImageField
from translations.models import Translatable

from offers.helpers.offer_helper import allowed_extensions, extension_error_message, fileSize


class Offer(Translatable):
    title = models.CharField(max_length=255)
    image = ResizedImageField(upload_to="offers", validators=[
        validators.FileExtensionValidator(
            allowed_extensions, extension_error_message),
        fileSize])

    class TranslatableMeta:
        fields = ["title"]

    class Meta:
        verbose_name_plural = "offers"

    def __str__(self) -> str:
        return self.title
