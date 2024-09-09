import uuid

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField
from translations.models import Translatable

allowed_extensions = ['jpg', 'png', 'jpeg', 'gif']
extension_error_message = "allowed format is :  'jpg', 'png', 'jpeg',  'gif' "


def fileSize(value):
    limit = 5 * 1024 * 1000
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MiB.')

def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError('Only PDF files are allowed.')

class Article(Translatable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    article_image = ResizedImageField(upload_to="article",
                                      validators=[
                                          validators.FileExtensionValidator(allowed_extensions,
                                                                            extension_error_message),
                                          fileSize
                                      ])
    article_title = models.CharField(max_length=255)
    article_text = models.TextField()
    article_writer = models.CharField(max_length=255)
    article_department = models.CharField(max_length=255)
    # article_details_text = models.TextField()
    isArchived = models.BooleanField(default=False)
    pdf_articale = models.FileField(
        upload_to='pdfs',
        null=True,
        blank=True,
        validators=[validate_pdf]  
    )
    class TranslatableMeta:
        fields = ['article_title', 'article_text', 'article_writer', 'article_department']

    class Meta:
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.article_title
