from rest_framework import serializers

from app.products.models import Category
from app.products.models import Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "product_count", "created_at"]
        read_only_fields = ["created_at", "product_count"]

    def get_product_count(self, obj) -> int:
        """Get count of products in category."""
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with nested category."""

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    is_low_stock = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name",
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

    def get_is_low_stock(self, obj) -> bool:
        """Check if product is low on stock."""
        return obj.is_low_stock()

    def get_profit_margin(self, obj):
        """Get profit margin percentage."""
        return str(obj.get_profit_margin())

    def create(self, validated_data):
        """Create product with current user as created_by."""
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update product and set updated_by to current user."""
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product list views."""

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    is_low_stock = serializers.SerializerMethodField()

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

    def get_is_low_stock(self, obj) -> bool:
        """Check if product is low on stock."""
        return obj.is_low_stock()
