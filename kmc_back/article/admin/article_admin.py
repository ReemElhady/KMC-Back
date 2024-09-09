from django.contrib import admin
from translations.admin import TranslatableAdmin, TranslationInline

from ..models.article_model import Article


class ArticleAdmin(TranslatableAdmin):
    list_display = ('article_title', 'created_at', 'isArchived',)
    search_fields = ('created_at', 'article_title', 'article_text', 'article_writer',
                     'article_department',)
    ordering = ('-created_at', 'isArchived')
    inlines = [TranslationInline]

    def make_archived(self, request, queryset):
        queryset.update(isArchived=True)

    def make_unarchived(self, request, queryset):
        queryset.update(isArchived=False)

    actions = [make_archived, make_unarchived]


admin.site.register(Article, ArticleAdmin)
