"""Tests for Product forms."""

import pytest

from app.products.forms import ProductFilterForm
from app.products.forms import ProductForm
from app.products.tests import CategoryFactory


@pytest.mark.django_db
class TestProductForm:
    """Test ProductForm."""

    def test_form_valid(self):
        """Test valid product form."""
        category = CategoryFactory()

        form_data = {
            "name": "Test Product",
            "description": "A test product",
            "sku": "TEST-SKU-001",
            "price": "99.99",
            "cost": "50.00",
            "stock_quantity": 100,
            "low_stock_threshold": 10,
            "category": category.id,
            "status": "active",
        }

        form = ProductForm(form_data)
        assert form.is_valid()

    def test_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            "name": "Test Product",
        }

        form = ProductForm(form_data)
        assert not form.is_valid()


@pytest.mark.django_db
class TestProductFilterForm:
    """Test ProductFilterForm."""

    def test_filter_form_empty(self):
        """Test filter form with no data."""
        form = ProductFilterForm(data={})
        assert form.is_valid()

    def test_filter_form_with_search(self):
        """Test filter form with search."""
        form_data = {"search": "laptop"}
        form = ProductFilterForm(form_data)
        assert form.is_valid()

    def test_filter_form_with_price_range(self):
        """Test filter form with price range."""
        form_data = {
            "min_price": "50",
            "max_price": "200",
        }
        form = ProductFilterForm(form_data)
        assert form.is_valid()
