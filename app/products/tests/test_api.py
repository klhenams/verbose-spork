"""Tests for Product API."""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from app.products.constants import ProductStatus
from app.products.models import Product
from app.products.tests import CategoryFactory
from app.products.tests import ProductFactory
from app.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestProductAPI:
    """Test Product API endpoints."""

    @pytest.fixture
    def client(self):
        """Create API client."""
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated API client."""
        user = UserFactory()
        client.force_authenticate(user=user)
        return client, user

    def test_list_products_requires_auth(self, client):
        """Test that listing products requires authentication."""
        response = client.get("/api/products/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_products(self, authenticated_client):
        """Test listing products."""
        client, _ = authenticated_client
        category = CategoryFactory()
        ProductFactory.create_batch(5, category=category)

        response = client.get("/api/products/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) <= 5  # noqa: PLR2004

    def test_pagination(self, authenticated_client):
        """Test pagination."""
        client, _ = authenticated_client
        ProductFactory.create_batch(25)

        response = client.get("/api/products/?page_size=10&page=1")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10  # noqa: PLR2004
        assert response.data["count"] >= 25  # noqa: PLR2004

    def test_filter_by_name(self, authenticated_client):
        """Test filtering by name."""
        client, _ = authenticated_client
        ProductFactory(name="Laptop")
        ProductFactory(name="Mouse")

        response = client.get("/api/products/?name=Laptop")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Laptop"

    def test_filter_by_sku(self, authenticated_client):
        """Test filtering by SKU."""
        client, _ = authenticated_client
        ProductFactory(sku="SKU-001")
        ProductFactory(sku="SKU-002")

        response = client.get("/api/products/?sku=SKU-001")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["sku"] == "SKU-001"

    def test_filter_by_category(self, authenticated_client):
        """Test filtering by category."""
        client, _ = authenticated_client
        category1 = CategoryFactory(name="Electronics")
        category2 = CategoryFactory(name="Books")
        ProductFactory(category=category1)
        ProductFactory(category=category2)

        response = client.get(f"/api/products/?category={category1.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_filter_by_status(self, authenticated_client):
        """Test filtering by status."""
        client, _ = authenticated_client
        ProductFactory(status=ProductStatus.ACTIVE)
        ProductFactory(status=ProductStatus.INACTIVE)

        response = client.get(f"/api/products/?status={ProductStatus.ACTIVE}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_filter_by_price_range(self, authenticated_client):
        """Test filtering by price range."""
        client, _ = authenticated_client
        ProductFactory(price=Decimal("50.00"))
        ProductFactory(price=Decimal("150.00"))

        response = client.get("/api/products/?min_price=100&max_price=200")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["price"] == "150.00"

    def test_filter_by_low_stock(self, authenticated_client):
        """Test filtering by low stock."""
        client, _ = authenticated_client
        ProductFactory(stock_quantity=5, low_stock_threshold=10)
        ProductFactory(stock_quantity=50, low_stock_threshold=10)

        response = client.get("/api/products/?is_low_stock=true")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_create_product(self, authenticated_client):
        """Test creating a product."""
        client, user = authenticated_client
        category = CategoryFactory()

        data = {
            "name": "New Product",
            "description": "A great product",
            "sku": "NEW-SKU-001",
            "price": "99.99",
            "cost": "50.00",
            "stock_quantity": 100,
            "low_stock_threshold": 10,
            "category": category.id,
            "status": ProductStatus.ACTIVE,
        }

        response = client.post("/api/products/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Product"
        assert response.data["created_by"] == user.id

    def test_retrieve_product(self, authenticated_client):
        """Test retrieving a product."""
        client, _ = authenticated_client
        product = ProductFactory()

        response = client.get(f"/api/products/{product.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product.id
        assert response.data["name"] == product.name

    def test_update_product(self, authenticated_client):
        """Test updating a product."""
        client, user = authenticated_client
        product = ProductFactory()

        data = {
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

        response = client.patch(
            f"/api/products/{product.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Product"
        assert response.data["updated_by"] == user.id

    def test_delete_product(self, authenticated_client):
        """Test deleting a product."""
        client, _ = authenticated_client
        product = ProductFactory()
        product_id = product.id

        response = client.delete(f"/api/products/{product_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(id=product_id).exists()
