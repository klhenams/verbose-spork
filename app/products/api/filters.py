import django_filters as filters
from django.db.models import F

from app.products.constants import ProductStatus
from app.products.models import Category
from app.products.models import Product


class ProductFilter(filters.FilterSet):
    """Filter for Product queryset."""

    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    sku = filters.CharFilter(
        field_name="sku",
        lookup_expr="icontains",
    )
    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
    )
    status = filters.ChoiceFilter(
        choices=ProductStatus.choices,
    )
    is_low_stock = filters.BooleanFilter(
        method="filter_low_stock",
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "status",
            "min_price",
            "max_price",
            "is_low_stock",
        ]

    def filter_low_stock(self, queryset, name, value):
        """Filter products by low stock status."""
        if value:
            return queryset.filter(
                stock_quantity__lt=F("low_stock_threshold"),
            )
        return queryset
