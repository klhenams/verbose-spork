"""Tests for Product views."""

import pytest
from django.urls import reverse
from rest_framework import status

from app.products.models import Product
from app.products.tests import CategoryFactory
from app.products.tests import ProductFactory
from app.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestProductListView:
    """Test ProductListView."""

    def test_list_view_requires_login(self, client):
        """Test that list view requires login."""
        response = client.get(reverse("products:list"))
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login

    def test_list_view_authenticated(self, client):
        """Test list view for authenticated user."""
        user = UserFactory()
        client.force_login(user)
        ProductFactory.create_batch(5)

        response = client.get(reverse("products:list"))
        assert response.status_code == status.HTTP_200_OK
        assert "products" in response.context

    def test_list_view_pagination(self, client):
        """Test pagination in list view."""
        user = UserFactory()
        client.force_login(user)
        ProductFactory.create_batch(25)

        response = client.get(reverse("products:list"))
        assert response.status_code == status.HTTP_200_OK
        paginator = response.context["paginator"]
        assert paginator.num_pages > 1

    def test_list_view_filter_by_search(self, client):
        """Test filtering by search."""
        user = UserFactory()
        client.force_login(user)
        ProductFactory(name="Laptop")
        ProductFactory(name="Mouse")

        response = client.get(reverse("products:list") + "?search=Laptop")
        assert response.status_code == status.HTTP_200_OK
        products = response.context["products"]
        assert len(products) == 1

    def test_list_view_filter_by_category(self, client):
        """Test filtering by category."""
        user = UserFactory()
        client.force_login(user)
        category = CategoryFactory()
        ProductFactory(category=category)
        ProductFactory()

        response = client.get(reverse("products:list") + f"?category={category.id}")
        assert response.status_code == status.HTTP_200_OK
        products = response.context["products"]
        assert len(products) == 1


@pytest.mark.django_db
class TestProductDetailView:
    """Test ProductDetailView."""

    def test_detail_view_requires_login(self, client):
        """Test that detail view requires login."""
        product = ProductFactory()
        response = client.get(reverse("products:detail", args=[product.id]))
        assert response.status_code == status.HTTP_302_FOUND

    def test_detail_view_authenticated(self, client):
        """Test detail view for authenticated user."""
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()

        response = client.get(reverse("products:detail", args=[product.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.context["product"] == product


@pytest.mark.django_db
class TestProductCreateView:
    """Test ProductCreateView."""

    def test_create_view_requires_login(self, client):
        """Test that create view requires login."""
        response = client.get(reverse("products:create"))
        assert response.status_code == status.HTTP_302_FOUND

    def test_create_product(self, client):
        """Test creating a product."""
        user = UserFactory()
        client.force_login(user)
        category = CategoryFactory()

        form_data = {
            "name": "New Product",
            "description": "A great product",
            "sku": "NEW-SKU-001",
            "price": "99.99",
            "cost": "50.00",
            "stock_quantity": 100,
            "low_stock_threshold": 10,
            "category": category.id,
            "status": "active",
        }

        response = client.post(reverse("products:create"), form_data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect after success
        assert Product.objects.filter(name="New Product").exists()


@pytest.mark.django_db
class TestProductUpdateView:
    """Test ProductUpdateView."""

    def test_update_product(self, client):
        """Test updating a product."""
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()

        form_data = {
            "name": "Updated Product",
            "description": product.description,
            "sku": product.sku,
            "price": "199.99",
            "cost": product.cost,
            "stock_quantity": product.stock_quantity,
            "low_stock_threshold": product.low_stock_threshold,
            "category": product.category.id,
            "status": product.status,
        }

        response = client.post(reverse("products:update", args=[product.id]), form_data)
        assert response.status_code == status.HTTP_302_FOUND
        product.refresh_from_db()
        assert product.name == "Updated Product"


@pytest.mark.django_db
class TestProductDeleteView:
    """Test ProductDeleteView."""

    def test_delete_product(self, client):
        """Test deleting a product."""
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()
        product_id = product.id

        response = client.post(reverse("products:delete", args=[product.id]))
        assert response.status_code == status.HTTP_302_FOUND
        assert not Product.objects.filter(id=product_id).exists()
