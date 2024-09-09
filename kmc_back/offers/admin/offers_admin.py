from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from offers.models.offer_model import Offer


class OffersAdmin(TranslatableAdmin):
    inlines = [TranslationInline]
   
    def has_add_permission(self, *args, **kwargs):
        return not Offer.objects.exists()


admin.site.register(Offer, OffersAdmin)
