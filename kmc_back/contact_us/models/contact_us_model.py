from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField
from translations.models import Translatable


def validate_phone(phone):
    if not phone[0:2] == '01' and not phone[0:2] == '02':
        raise ValidationError('phone number is not valid.')


def fileSize(value):
    limit = 5 * 1024 * 1000
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MiB.')


allowed_extensions = ['jpg', 'png', 'jpeg', 'gif']
extension_error_message = "allowed format is :  'jpg', 'png', 'jpeg',  'gif' "


class ContactUs(Translatable):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    image = ResizedImageField(upload_to="contact-us/main-page",
                              validators=
                              [
                                  validators.FileExtensionValidator(allowed_extensions, extension_error_message),
                                  fileSize
                              ])
    phone = models.CharField(max_length=11, help_text="Max Length is 11 numbers.", validators=[validate_phone])
    phone1 = models.CharField(max_length=11, help_text="Max Length is 11 numbers.", validators=[validate_phone],
                              blank=True, null=True)
    email = models.EmailField()
    address = models.TextField()
    address_url = models.URLField(null=True, blank=True)

    class TranslatableMeta:
        fields = ['title', 'sub_title']

    class Meta:
        verbose_name_plural = "Contact Us Page"

    def __str__(self):
        return self.title
