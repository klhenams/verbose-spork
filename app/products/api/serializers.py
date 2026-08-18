from rest_framework import serializers

from app.products.models import Category
from app.products.models import Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model.

    Expects `product_count` to be annotated on the QuerySet via
    `.annotate(product_count=Count('products'))`.
    """

    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["id", "name", "description", "product_count", "created_at"]
        read_only_fields = ["created_at", "product_count"]


class BaseProductSerializer(serializers.ModelSerializer):
    """Base serializer providing common field definitions for Product variants."""

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    is_low_stock = serializers.ReadOnlyField()
    profit_margin = serializers.DecimalField(
        source="get_profit_margin",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        default=serializers.CharField(source="created_by.username", read_only=True),
        read_only=True,
    )
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name",
        default=serializers.CharField(source="updated_by.username", read_only=True),
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "sku",
            "price",
            "cost",
            "profit_margin",
            "stock_quantity",
            "low_stock_threshold",
            "is_low_stock",
            "category",
            "category_name",
            "status",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
            "is_low_stock",
            "profit_margin",
        ]


class ProductSerializer(BaseProductSerializer):
    """Standard detail serializer handling automated user auditing on write."""

    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    updated_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    def update(self, instance, validated_data):
        """Ensure updated_by is explicitly reassigned on instance updates."""
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product list views."""

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "price",
            "stock_quantity",
            "category_name",
            "status",
            "is_low_stock",
            "created_at",
        ]
        read_only_fields = fields


class ProductWorkflowSerializer(BaseProductSerializer):
    """Serializer tailored for workflow tasks with Temporal-managed status."""

    class Meta(BaseProductSerializer.Meta):
        read_only_fields = [*BaseProductSerializer.Meta.read_only_fields, "status"]
