from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category
from .models import Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "product_count", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(
        description=_("Products"),
    )
    def product_count(self, obj) -> int:
        """Get product count for category."""
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "status",
        "is_low_stock_indicator",
        "created_at",
    ]
    list_filter = [
        "status",
        "category",
        "created_at",
        # "is_low_stock",
    ]
    search_fields = ["name", "sku", "description"]
    readonly_fields = [
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
        "profit_margin_display",
    ]
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("name", "description", "category", "sku"),
            },
        ),
        (
            _("Pricing & Inventory"),
            {
                "fields": (
                    "price",
                    "cost",
                    "profit_margin_display",
                    "stock_quantity",
                    "low_stock_threshold",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Tracking"),
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(
        description=_("Stock Status"),
    )
    def is_low_stock_indicator(self, obj) -> str:
        """Show low stock indicator."""
        if obj.is_low_stock():
            return "⚠️ Low Stock"
        return "✓ OK"

    @admin.display(
        description=_("Profit Margin"),
    )
    def profit_margin_display(self, obj) -> str:
        """Display profit margin."""
        margin = obj.get_profit_margin()
        return f"{margin}%"

    def save_model(self, request, obj, form, change):
        """Set created_by or updated_by on save."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
