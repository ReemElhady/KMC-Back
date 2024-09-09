from django.core import validators
from django.core.validators import ValidationError
from django.db import models
from django_resized import ResizedImageField


def fileSize(value):
    limit = 10 * 1024 * 1000
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 10 MB.")


allowed_extensions = ["jpg", "png", "jpeg", "gif", "mp4", "mkv"]
allowed_images = ["jpg", "png", "jpeg", "gif"]
extension_error_message = (
    "allowed format is :  'jpg', 'png', 'jpeg',  'gif', 'mp4', 'mkv'"
)
image_extension_error_message = "allowed format is :  'jpg', 'png', 'jpeg',  'gif'"


class HomeSwiper(models.Model):
    media = models.FileField(
        upload_to="home/home-swiper",
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            fileSize,
        ],
    )

    mobile_view_media = models.FileField(
        upload_to="home/home-swiper",
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            fileSize,
        ],
        null=True,
        blank=True,
    )

    link = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Home Swiper"

    def __str__(self):
        return self.media.name


class HomeDetails(models.Model):
    about_us_title = models.CharField(max_length=255, default="")
    categories_caption = models.TextField(null=True, blank=True)
    about_us_1_caption = models.TextField(null=True, blank=True)
    about_us_2_caption = models.TextField(null=True, blank=True)
    about_us_1_image = ResizedImageField(
        upload_to="home/home-details",
        validators=[
            validators.FileExtensionValidator(
                allowed_images, image_extension_error_message
            ),
            fileSize,
        ],
        null=True,
        blank=True,
    )
    about_us_2_image = ResizedImageField(
        upload_to="home/home-details",
        validators=[
            validators.FileExtensionValidator(
                allowed_images, image_extension_error_message
            ),
            fileSize,
        ],
        null=True,
        blank=True,
    )

    # about_us_3_image = ResizedImageField(upload_to="home/home-details",
    #                                      validators=
    #                                      [
    #                                          validators.FileExtensionValidator(allowed_images,
    #                                                                            image_extension_error_message),
    #                                          fileSize
    #                                      ], null=True, blank=True)
    # about_us_4_image = ResizedImageField(upload_to="home/home-details",
    #                                      validators=
    #                                      [
    #                                          validators.FileExtensionValidator(allowed_images,
    #                                                                            image_extension_error_message),
    #                                          fileSize
    #                                      ], null=True, blank=True)

    class Meta:
        verbose_name_plural = "Home Details"


class PopularProduct(models.Model):
    product = models.OneToOneField(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="popular_products",
        unique=True,
        limit_choices_to={"is_archived": False},
    )

    def __str__(self):
        return self.product.__str__()
