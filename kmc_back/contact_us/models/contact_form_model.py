from django.db import models

from .contact_us_model import validate_phone


class ContactForm(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=11, help_text="Maximum Length is 11 numbers.", validators=[validate_phone])
    subject = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        verbose_name_plural = "Contact Us Forms"
