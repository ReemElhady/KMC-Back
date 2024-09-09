from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from user.models.user_model import User
from django.utils.translation import gettext as _
# from user.models.otp_models import OTP


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['phone', 'name']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'email')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2')
        }),
    )
    search_fields = ('phone', 'name')


admin.site.register(User, UserAdmin)
# admin.site.register(OTP)
