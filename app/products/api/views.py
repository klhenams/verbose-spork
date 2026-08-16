from django.db import models
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from app.products.models import Category
from app.products.models import Product

from .filters import ProductFilter
from .serializers import CategorySerializer
from .serializers import ProductListSerializer
from .serializers import ProductSerializer


class CategoryViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet for Category CRUD operations."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["name"]

    def get_queryset(self):
        """Get queryset with product counts."""
        return self.queryset.annotate(
            product_count=models.Count("products"),
        )


class ProductViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet for Product CRUD operations with filtering and pagination."""

    queryset = Product.objects.select_related(
        "category",
        "created_by",
        "updated_by",
    )
    filterset_class = ProductFilter

    def get_serializer_class(self):
        """Use lightweight serializer for list actions."""
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        """Create product with current user."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Update product and set updated_by to current user."""
        serializer.save(updated_by=self.request.user)
