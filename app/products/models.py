from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import ForeignKey
from django.db.models import Index
from django.db.models import Model
from django.db.models import PositiveIntegerField
from django.db.models import TextField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app.products.constants import ProductStatus

User = get_user_model()


class Category(Model):
    """Product category."""

    name = CharField(_("name"), max_length=255, unique=True)
    description = TextField(_("description"), blank=True)
    created_at = DateTimeField(_("created at"), auto_now_add=True)
    updated_at = DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(Model):
    """Product model with complete CRUD functionality."""

    # Basic info
    name = CharField(_("name"), max_length=255)
    description = TextField(_("description"))
    sku = CharField(_("SKU"), max_length=100, unique=True)

    # Pricing & Inventory
    price = DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    cost = DecimalField(
        _("cost"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Cost price for internal tracking"),
    )
    stock_quantity = PositiveIntegerField(_("stock quantity"), default=0)
    low_stock_threshold = PositiveIntegerField(
        _("low stock threshold"),
        default=10,
        help_text=_("Alert when stock falls below this"),
    )

    # Category
    category = ForeignKey(
        Category,
        on_delete=CASCADE,
        related_name="products",
        verbose_name=_("category"),
    )

    # Status & Tracking
    status = CharField(
        _("status"),
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.ACTIVE,
    )
    created_by = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="products_created",
        verbose_name=_("created by"),
    )
    updated_by = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="products_updated",
        verbose_name=_("updated by"),
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = DateTimeField(_("created at"), auto_now_add=True)
    updated_at = DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["sku"], name="product_sku_idx"),
            Index(fields=["status"], name="product_status_idx"),
            Index(fields=["category"], name="product_category_idx"),
            Index(fields=["-created_at"], name="product_created_idx"),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Get URL for product detail view.

        Returns:
            str: URL for product detail.
        """
        return reverse("products:detail", kwargs={"pk": self.id})

    def is_low_stock(self) -> bool:
        """Check if product is below low stock threshold."""
        return self.stock_quantity < self.low_stock_threshold

    def get_profit_margin(self) -> Decimal:
        """Calculate profit margin percentage."""
        if self.cost == 0:
            return Decimal("0.00")
        margin = ((self.price - self.cost) / self.cost) * 100
        return margin.quantize(Decimal("0.01"))
