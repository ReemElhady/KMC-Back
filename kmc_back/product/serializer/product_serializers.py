from rest_framework import serializers

from ..models.product_models import Type, Product, ProductImage, ProductVideoUrl, WishList, Branch, SubBranch, \
    Brand, ProductItem


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("image",)


class ProductUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideoUrl
        fields = ("url",)


class ProductItemSerializer(serializers.ModelSerializer):
    product_item_title = serializers.CharField(source='product.product_item_title')

    class Meta:
        model = ProductItem
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("name", 'id', 'image')


class SubBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubBranch
        fields = ("name", 'id')


class BranchSerializer(serializers.ModelSerializer):
    branch_sub_branches = SubBranchSerializer(many=True)

    class Meta:
        model = Branch
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    product_item = ProductItemSerializer(many=True)
    product_item_title = serializers.CharField()

    def get_main_image(self, obj):
        try:
            return obj.product_image.get(is_main=True).image.url
        except:
            return "doesn't exists"

    def get_is_wishlist(self, obj):
        user = self.context.get("user")
        if not user or user.is_anonymous:  # Handle the case where user is None or anonymous
            return False
        return ReturnIsWishlisted(user, obj)

    # def get_branches(self, obj):
    #Ensure that the sale percentage handled correctly
    final_price = serializers.SerializerMethodField()
    def get_final_price(self, obj):
        return obj.get_final_price()

    class Meta:
        model = Product
        fields = [
            'id', 'branch', 'sub_branch', 'type', 'brand', 'title', 
            'description', 'price', 'sale_price', 'sale_percentage', 
            'stock', 'rate', 'is_archived', 'created_at', 'product_item_title', 
            'weight', 'number_of_boxes', 'main_image', 'is_wishlist', 'product_item', 
            'final_price'
        ]



# class ReviewSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='user.name')
#
#     class Meta:
#         model = Review
#         fields = "__all__"
#

class ProductDetailsSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    product_url = ProductUrlSerializer(many=True)
    # reviews_count = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    # reviewed = serializers.SerializerMethodField()
    # reviews_list = serializers.SerializerMethodField()
    product_item = ProductItemSerializer(many=True)
    product_item_title = serializers.CharField()

    # def get_reviews_list(self, obj):
    #     return ReviewSerializer(obj.product_review.all()[:10], many=True).data

    def get_product_image(self, obj):
        return ProductImageSerializer(obj.product_image.all(), many=True).data

    # def get_reviewed(self, obj):
    #     if self.context.get('user').is_anonymous:
    #         return False
    #     return Review.objects.filter(product=obj, user=self.context.get('user')).exists()

    def get_is_wishlist(self, obj):
        return ReturnIsWishlisted(self.context.get("user"), obj)

    # def get_reviews_count(self, obj):
    #     return obj.product_review.count()

    def get_related_products(self, obj):
        lang = self.context.get("lang")
        user = self.context.get("user")
        query = Product.objects.filter(sub_branch=obj.sub_branch).exclude(id=obj.id).translate(lang)
        return ProductListSerializer(query, many=True, context={'user': user}).data

    class Meta:
        model = Product
        fields = "__all__"


class WishListSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    def get_product_details(self, obj):
        lang = self.context.get("lang")
        product = Product.objects.translate(lang).get(id=obj.product.id)
        return WishlistProductSerializer(product).data

    class Meta:
        model = WishList
        fields = "__all__"


class WishlistProductSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()

    def get_main_image(self, obj):
        try:
            return obj.product_image.get(is_main=True).image.url
        except:
            return "doesn't exists"

    class Meta:
        model = Product
        fields = ('title', 'main_image', 'id', 'type', 'price', 'sale_price', 'sale_percentage')


def ReturnIsWishlisted(user, obj):
    if user.is_anonymous:
        return False
    return WishList.objects.filter(user=user, product=obj).exists()


class PopularProductSerializer(serializers.Serializer):
    product = ProductListSerializer(read_only=True)



class LowInStockProductSerializer(serializers.Serializer):
    product = ProductListSerializer(read_only=True)
