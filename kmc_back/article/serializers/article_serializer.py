from rest_framework import serializers

from ..models.article_model import Article


class ArticleListSerializer(serializers.ModelSerializer):
    article_image = serializers.CharField(source="article_image.url")

    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%-d\n%b")

    class Meta:
        model = Article
        fields = '__all__'


class ArticleDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%-d\n%b")

    class Meta:
        model = Article
        fields = '__all__'
