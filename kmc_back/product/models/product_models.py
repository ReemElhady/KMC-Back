import os
import uuid
from urllib.parse import urlparse, parse_qs

from django.core import validators
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django_resized import ResizedImageField
from translations.models import Translatable

from product.uitlity.productUtility import (
    allowed_extensions,
    extension_error_message,
    file_size,
)
from user.models import User


def get_product_image_path(instance, filename):
    return os.path.join("product", instance.product.title, filename)


def get_type_image_path(instance, filename):
    return os.path.join("type", instance.name, filename)


def get_brand_image_path(instance, filename):
    return os.path.join("brand", instance.name, filename)


# Create your models here.
class Type(Translatable):
    name = models.CharField(max_length=255)
    image = ResizedImageField(
        upload_to=get_type_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )

    category_image = ResizedImageField(
        upload_to=get_type_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )

    category_details_image = ResizedImageField(
        upload_to=get_type_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )

    hover_image = ResizedImageField(
        upload_to=get_type_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )
    display_ordering = models.PositiveIntegerField(null=True, blank=True)

    class TranslatableMeta:
        fields = ["name"]

    def __str__(self):
        return self.name


class Branch(Translatable):
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="type_branch")
    name = models.CharField(max_length=255)
    image = ResizedImageField(
        upload_to=get_type_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )

    class TranslatableMeta:
        fields = ["name"]

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class SubBranch(Translatable):
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="branch_sub_branches"
    )
    name = models.CharField(max_length=255)

    class TranslatableMeta:
        fields = ["name"]

    class Meta:
        verbose_name_plural = "Sub Branches"

    def __str__(self):
        return self.name


class Brand(Translatable):
    name = models.CharField(max_length=255)
    image = ResizedImageField(
        upload_to=get_brand_image_path,
        null=True,
        blank=True,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )

    class TranslatableMeta:
        fields = ["name"]

    def __str__(self):
        return self.name


class Product(Translatable):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=255
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="product_branch"
    )
    sub_branch = models.ForeignKey(
        SubBranch,
        on_delete=models.CASCADE,
        related_name="product_sub_branch",
        null=True,
        blank=True,
    )
    type = models.ForeignKey(
        Type, on_delete=models.CASCADE, related_name="product_type"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="product_brand"
    )   
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    sale_price = models.FloatField(
        validators=[MinValueValidator(0.0)], default=0, null=True, blank=True
    )
    sale_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    ) #adding percentage option
    stock = models.PositiveIntegerField()
    rate = models.PositiveIntegerField(default=3, validators=[MaxValueValidator(5)])
    # point_price = models.PositiveIntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    product_item_title = models.CharField(max_length=255, null=True, blank=True)
    weight = models.FloatField(
        validators=[MinValueValidator(0.001)],
        default=0.1,
        help_text="1=1Kg, 0.1=100gm, 0.01=10gm, 0.001=1gm",
    )
    number_of_boxes = models.PositiveIntegerField(default=1)
    
    def save(self, *args, **kwargs):
        # Ensure sale_percentage and sale_price are only calculated if the other has a valid value
        if self.sale_percentage is not None and self.sale_percentage > 0:
            self.sale_price = self.price * (1 - self.sale_percentage / 100)
        elif self.sale_price is not None and self.sale_price > 0:
            self.sale_percentage = (self.price - self.sale_price) / self.price * 100
        else:
            # No sale, so both sale_price and sale_percentage should be set to None
            self.sale_price = None
            self.sale_percentage = None
        super(Product, self).save(*args, **kwargs)

    def get_final_price(self):
        if self.sale_price is not None:
            return self.sale_price
        return self.price
    
    class TranslatableMeta:
        fields = ["title", "description", "product_item_title"]

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    image = ResizedImageField(
        upload_to=get_product_image_path,
        validators=[
            validators.FileExtensionValidator(
                allowed_extensions, extension_error_message
            ),
            file_size,
        ],
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_image"
    )
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.title} - {self.image.name}"

    # Check if there is more or none is_main images
    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).exclude(
                id=self.id
            ).update(is_main=False)
        else:
            is_main_images = (
                ProductImage.objects.filter(product=self.product, is_main=True)
                .exclude(id=self.id)
                .count()
            )
            if not is_main_images:
                self.is_main = True
        super().save(*args, **kwargs)


class ProductVideoUrl(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_url", null=True
    )
    url = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Product Video Urls"

    def save(self, *args, **kwargs):
        try:
            parsed_url = urlparse(self.url)
            video_id = parse_qs(parsed_url.query).get("v")
            if video_id:
                video_id = video_id[0]
            else:
                video_id = self.url.split("/")[-1]
            self.url = f"https://www.youtube.com/embed/{video_id}"
        except:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title} - {self.url}"


class WishList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_wishlist"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_wishlist"
    )

    class Meta:
        unique_together = (("product", "user"),)

    def __str__(self):
        return self.user.name + " - " + self.product.title


class ProductItem(Translatable):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_item"
    )
    species = models.CharField(max_length=255)
    stock = models.PositiveIntegerField()

    class TranslatableMeta:
        fields = ["species"]

    def __str__(self):
        return f"{self.product.title} {self.species}"

    def save(self, *args, **kwargs):
        stock = (
            ProductItem.objects.filter(product=self.product)
            .exclude(id=self.id)
            .aggregate(Sum("stock"))
        )
        if stock.get("stock__sum"):
            self.product.stock = stock.get("stock__sum", 0) + self.stock
        else:
            self.product.stock = self.stock
        self.product.save()
        super().save(*args, **kwargs)

# class Review(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_review')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
#     content = models.TextField(null=True, blank=True)
#     rate = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
#
#     class Meta:
#         unique_together = (("product", "user"),)

# @receiver(post_save, sender=Review, dispatch_uid="create_review")
# def create_review(sender, instance, **kwargs):
#     if kwargs.get("created"):
#         product_rate = Review.objects.filter(product=instance.product).aggregate(product_rate=Avg('rate'))
#         instance.product.rate = round(product_rate['product_rate'])
#         instance.product.save(update_fields=["rate"])
#
#
# @receiver(post_delete, sender=Review, dispatch_uid="delete_review")
# def delete_review(sender, instance, **kwargs):
#     if kwargs.get("deleted"):
#         product_rate = Review.objects.filter(product=instance.product).aggregate(product_rate=Avg('rate'))
#         instance.product.rate = round(product_rate['product_rate'])
#         instance.product.save(update_fields=["rate"])
