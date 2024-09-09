from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from ..models.contact_form_model import ContactForm
from ..models.contact_us_model import ContactUs


class ContactUsAdmin(TranslatableAdmin):
    def has_add_permission(self, *args, **kwargs):
        return not ContactUs.objects.exists()

    inlines = [TranslationInline]


class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject')
    search_fields = ('name', 'email', 'subject', 'phone')
    ordering = ('id',)


admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(ContactForm, FormAdmin)
