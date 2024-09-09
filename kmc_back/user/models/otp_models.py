# from django.db import models
# from django_extensions.db.models import TimeStampedModel
# from django.conf import settings
#
# from user.helpers.user_helpers import create_activation_code
#
#
# class OTP(TimeStampedModel):
#     code = models.CharField(max_length=6)
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.code
#
#     def save(self, *args, **kwargs):
#         self.code = create_activation_code()
#         super().save(*args, **kwargs)
#
#     class Meta:
#         verbose_name_plural = 'OTPs'