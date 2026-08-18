from asgiref.sync import async_to_sync
from django.db import models
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.products.constants import ProductStatus
from app.products.models import Category
from app.products.models import Product
from app.products.workflows.workflows import ProductPriceOnboardingWorkflow
from config.temporal_client import TemporalClientManager

from .filters import ProductFilter
from .serializers import CategorySerializer
from .serializers import ProductListSerializer
from .serializers import ProductSerializer
from .serializers import ProductWorkflowSerializer


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

    queryset = Product.objects.filter(
        status=ProductStatus.ACTIVE,
    ).select_related(
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


class ProductCreateViewSet(CreateModelMixin, GenericViewSet):
    """Create products."""

    queryset = Product.objects.select_related(
        "category",
        "created_by",
        "updated_by",
    )
    serializer_class = ProductWorkflowSerializer

    def perform_create(self, serializer):
        product = serializer.save(
            created_by=self.request.user,
            status=ProductStatus.PENDING_PRICING,
        )

        # Read optional test parameters from request payload
        timeout_seconds = self.request.data.get("test_timeout_seconds", 86400)
        should_fail_publish = self.request.data.get("test_should_fail_publish", False)

        async def start_workflow():
            client = await TemporalClientManager.get_client()
            await client.start_workflow(
                ProductPriceOnboardingWorkflow.run,
                {
                    "product_id": product.pk,
                    "timeout_seconds": timeout_seconds,
                    "should_fail_publish": should_fail_publish,
                },
                id=f"product-onboarding-{product.pk}",
                task_queue="product-tasks",
            )

        async_to_sync(start_workflow)()

    @action(detail=True, methods=["get"], url_path="pricing-suggestion")
    def pricing_suggestion(self, request, pk=None):
        """Fetch real-time pricing suggestion from running Temporal workflow."""

        async def query_workflow():
            client = await TemporalClientManager.get_client()
            handle = client.get_workflow_handle(f"product-onboarding-{pk}")
            return await handle.query(
                ProductPriceOnboardingWorkflow.get_pricing_recommendation,
            )

        suggestion = async_to_sync(query_workflow)()
        return Response({"suggestion": suggestion}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve-price")
    def approve_price(self, request, pk=None):
        """Signal running workflow to accept or override suggested price."""
        chosen_price = request.data.get("price")
        if chosen_price is None:
            return Response(
                {"error": "Field 'price' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        async def signal_workflow():
            client = await TemporalClientManager.get_client()
            handle = client.get_workflow_handle(f"product-onboarding-{pk}")
            await handle.signal(
                ProductPriceOnboardingWorkflow.approve_suggested_price,
                float(chosen_price),
            )

        async_to_sync(signal_workflow)()
        return Response(
            {"detail": "Price signal sent. Product is being published."},
            status=status.HTTP_200_OK,
        )
