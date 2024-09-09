from django.db.models import Q
from django_filters import rest_framework as filters, OrderingFilter

from product.models.product_models import Product


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    type = NumberInFilter(field_name="type_id", lookup_expr="in")
    brand = NumberInFilter(field_name="brand_id", lookup_expr="in")
    title = filters.CharFilter(method="search_by_title")
    sale_price = filters.NumberFilter(field_name="sale_price", lookup_expr="gt")
    sale = filters.CharFilter(method="get_sales_product")

    def get_sales_product(self, queryset, name, value):
        return queryset.filter(sale_price__gt=0)

    def search_by_title(self, queryset, name, value):
        return queryset.probe(["en", "ar"]).filter(title__icontains=value)

    def filter_by_branch_and_sub_branch(self, queryset):
        branch = (
            list(map(int, self.request.query_params.get("branch").split(",")))
            if self.request.query_params.get("branch")
            else []
        )
        sub_branch = (
            list(map(int, self.request.query_params.get("sub_branch").split(",")))
            if self.request.query_params.get("sub_branch")
            else []
        )

        if not branch and not sub_branch:
            return queryset

        filter_by_branch = queryset.probe(["en", "ar"]).filter(Q(branch__id__in=branch))
        filter_by_subbranch = queryset.probe(["en", "ar"]).filter(Q(sub_branch__id__in=sub_branch))

        # Union 2 queries
        qs = filter_by_branch | filter_by_subbranch

        return qs

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        qs = self.filter_by_branch_and_sub_branch(qs)

        return qs


    sort = OrderingFilter(
        fields=(
            ("created_at", "date"),
            ("price", "price"),
            # and any model field you want to sort based on
        )
    )

    class Meta:
        model = Product
        fields = [
            "type",
            "brand",
            "sale",
            "max_price",
            "min_price",
            "sale_price",
        ]
