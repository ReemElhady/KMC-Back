from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from footer.models.service_model import Service


class ServiceAdmin(TranslatableAdmin):
    list_display = ('title',)
    search_fields = ('title', 'description')
    readonly_fields = ('slug',)

    inlines = [TranslationInline]

    def has_add_permission(self, *args, **kwargs):
        return Service.objects.count() < 4


admin.site.register(Service, ServiceAdmin)
