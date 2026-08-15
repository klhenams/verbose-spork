from django.db import models
from django_filters import rest_framework as filters
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from app.products.models import Category
from app.products.models import Product

from .serializers import CategorySerializer
from .serializers import ProductListSerializer
from .serializers import ProductSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for product list views."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


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
        choices=Product.STATUS_CHOICES,
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
                stock_quantity__lt=models.F("low_stock_threshold"),
            )
        return queryset


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
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend]
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
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend]
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
