"""Tests for Product models."""

from decimal import Decimal

import pytest
from django.db import IntegrityError

from app.products.constants import ProductStatus
from app.products.tests import CategoryFactory
from app.products.tests import ProductFactory


@pytest.mark.django_db
class TestCategory:
    """Test Category model."""

    def test_category_creation(self):
        """Test creating a category."""
        category = CategoryFactory(name="Electronics")
        assert category.name == "Electronics"
        assert str(category) == "Electronics"

    def test_category_string_representation(self):
        """Test category string representation."""
        category = CategoryFactory()
        assert str(category) == category.name


@pytest.mark.django_db
class TestProduct:
    """Test Product model."""

    def test_product_creation(self):
        """Test creating a product."""
        product = ProductFactory(name="Laptop", sku="SKU-001")
        assert product.name == "Laptop"
        assert product.sku == "SKU-001"
        assert str(product) == "Laptop"

    def test_product_string_representation(self):
        """Test product string representation."""
        product = ProductFactory()
        assert str(product) == product.name

    def test_is_low_stock(self):
        """Test low stock check."""
        product = ProductFactory(stock_quantity=5, low_stock_threshold=10)
        assert product.is_low_stock() is True

        product.stock_quantity = 15
        assert product.is_low_stock() is False

    def test_get_profit_margin(self):
        """Test profit margin calculation."""
        product = ProductFactory(price=Decimal("100.00"), cost=Decimal("60.00"))
        margin = product.get_profit_margin()
        assert margin == Decimal("66.67")

    def test_get_profit_margin_zero_cost(self):
        """Test profit margin when cost is zero."""
        product = ProductFactory(price=Decimal("100.00"), cost=Decimal("0.00"))
        margin = product.get_profit_margin()
        assert margin == Decimal("0.00")

    def test_product_absolute_url(self):
        """Test product absolute URL."""
        product = ProductFactory()
        assert product.get_absolute_url() == f"/products/{product.id}/"

    def test_product_status_choices(self):
        """Test product status choices."""
        product = ProductFactory(status=ProductStatus.ACTIVE)
        assert product.status == ProductStatus.ACTIVE

        product.status = ProductStatus.DISCONTINUED
        assert product.status == ProductStatus.DISCONTINUED

    def test_product_timestamps(self):
        """Test product creation and update timestamps."""
        product = ProductFactory()
        assert product.created_at is not None
        assert product.updated_at is not None
        assert product.created_at <= product.updated_at

    def test_product_sku_uniqueness(self):
        """Test that SKU must be unique."""
        sku = "UNIQUE-SKU"
        ProductFactory(sku=sku)

        with pytest.raises(IntegrityError):  # IntegrityError or similar
            ProductFactory(sku=sku)

    def test_category_relationship(self):
        """Test category relationship."""
        category = CategoryFactory()
        product = ProductFactory(category=category)
        assert product.category == category
        assert product in category.products.all()
