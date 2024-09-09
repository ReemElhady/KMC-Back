from django.db import models
from django.utils.text import slugify

from translations.models import Translatable


class Service(Translatable):
    slug = models.SlugField(null=False, blank=True, editable=False)
    title = models.CharField(max_length=255, verbose_name="Service Title", unique=True)
    description = models.TextField(verbose_name="Service Description")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class TranslatableMeta:
        fields = ['title', 'description']
