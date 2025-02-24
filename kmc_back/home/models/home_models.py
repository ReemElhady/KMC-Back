from django.core import validators
from django.core.validators import ValidationError, EmailValidator, RegexValidator
from django.db import models
from django_resized import ResizedImageField
from django.utils import timezone
from django.core.exceptions import ValidationError

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


def validate_phone(phone):
    if not phone[0:2] == '01' and not phone[0:2] == '02':
        raise ValidationError('phone number is not valid.')

class HomeSwiper(models.Model):
    POSITION_CHOICES = [
        ('top', 'Top Section'),
        ('middle', 'Middle Section'),
        ('bottom', 'Bottom Section'),
        ('flashSale', 'Flash Sale Section'),
        ('bookDemo', 'Book Demo Section'),
    ]

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

    # New field to define the position
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='top',  # Default to top section
        null=True,
    )

    class Meta:
        verbose_name_plural = "Home Swiper"

    def __str__(self):
        return self.position

# class HomeSwiper(models.Model):
#     media = models.FileField(
#         upload_to="home/home-swiper",
#         validators=[
#             validators.FileExtensionValidator(
#                 allowed_extensions, extension_error_message
#             ),
#             fileSize,
#         ],
#     )

#     mobile_view_media = models.FileField(
#         upload_to="home/home-swiper",
#         validators=[
#             validators.FileExtensionValidator(
#                 allowed_extensions, extension_error_message
#             ),
#             fileSize,
#         ],
#         null=True,
#         blank=True,
#     )

#     link = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True,
#     )

#     class Meta:
#         verbose_name_plural = "Home Swiper"

#     def __str__(self):
#         return self.media.name


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

class LowStockProduct(models.Model):
    product = models.OneToOneField(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="low_stock_products",
        unique=True,
        limit_choices_to={"is_archived": False},
    )

    def __str__(self):
        return self.product.__str__()

class Ad(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
class FlashSale(models.Model):
    title = models.CharField(max_length=255)  # Optional: Name of the sale
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # To toggle the sale
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_sale_active(self):
        """Check if the flash sale is currently active."""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class GalleryImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='home/gallery/',
            validators=[
            validators.FileExtensionValidator(
                allowed_images, image_extension_error_message
            ),
            fileSize,
        ],
        null=True,
        blank=True,)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DemoBooking(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")]
    )
    phone = models.CharField(
        max_length=11,
        validators=[validate_phone],
    )
    device_name = models.CharField(max_length=250)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Booking Demo Forms"
        
    def __str__(self):
        return self.full_name


class DemoBookingPage(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    image = ResizedImageField(upload_to="book-demo/main-page",
                              validators=
                              [
                                  validators.FileExtensionValidator(allowed_extensions, extension_error_message),
                                  fileSize
                              ])
    # add new field for mobile view
    mobile_view_media = models.FileField(
        upload_to="book-demo/main-page",
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            fileSize,
        ],
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name_plural = "Booking Demo page"