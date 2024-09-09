from django.db import models

from translations.models import Translatable


class FAQ(Translatable):
    question = models.CharField(max_length=500, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")

    def __str__(self):
        return self.question

    class TranslatableMeta:
        fields = ['question', 'answer']

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
