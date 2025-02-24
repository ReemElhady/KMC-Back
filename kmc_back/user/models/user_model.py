from django.contrib.auth.models import (
    PermissionsMixin,
    BaseUserManager,
    AbstractBaseUser,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from wasage.wasage import Wasage

# from user.helpers.user_helpers import sendOtp
# from user.models.otp_models import OTP


class UserManager(BaseUserManager):
    def validate_phone_number(self, phone):
        if not phone:
            message = "Users must have a phone number"
            return message, False
        if not phone[0:2] == "01":
            message = "Phone number is incorrect"
            return message, False
        return "", True

    def create_user(self, phone, password=None, **extra_fields):
        """Creates and saves a new user"""
        message, valid = self.validate_phone_number(phone)
        if not valid:
            raise ValueError(message)
        try:
            user = User.objects.get(phone=phone, is_active=False)
            user.name = extra_fields["name"]
            user.email = extra_fields["email"]

            # otp, created = OTP.objects.get_or_create(user=user)
            # if not created:
            #     otp.save()
            # sendOtp(otp, user.phone)

        except:
            user = self.model(phone=phone, **extra_fields)
            user.is_active = False

        user.set_password(password)
        user.save()
        # wasage_response = Wasage.send_otp(user.id)

        return {
            "user": user,
            # "wasage_response": wasage_response,
        }

    def create_superuser(self, phone, password):
        """Creates and saves a new superuser"""
        user = self.create_user(phone, password).get("user")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using phone instead of username"""

    phone = models.CharField(
        max_length=11, unique=True, help_text="Maximum length is 11 numbers"
    )
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"


# @receiver(post_save, sender=User, dispatch_uid="create_user_otp")
# def create_user_otp(sender, instance, **kwargs):
#     from user.models.otp_models import OTP
#
#     if kwargs.get("created"):
#         otp = OTP.objects.create(user=instance, code=create_activation_code())
#         sendOtp(otp, instance.phone)
