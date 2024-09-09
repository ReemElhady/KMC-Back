from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from FAQ.models.FAQ_model import FAQ


class FAQAdmin(TranslatableAdmin):
    list_display = ('question',)
    search_fields = ('question', 'answer')

    inlines = [TranslationInline]


admin.site.register(FAQ, FAQAdmin)
