from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import ProductFilterForm
from .forms import ProductForm
from .models import Product

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class ProductListView(LoginRequiredMixin, ListView):
    """List products with pagination and filtering."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset based on form input."""
        queryset = Product.objects.select_related(
            "category",
            "created_by",
        ).all()

        # Search by name or SKU
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search),
            )

        # Filter by category
        category = self.request.GET.get("category", "").strip()
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by status
        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)

        # Filter by price range
        min_price = self.request.GET.get("min_price", "").strip()
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                logger.warning("Invalid min_price parameter received: %r", min_price)

        max_price = self.request.GET.get("max_price", "").strip()
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                logger.warning("Invalid max_price parameter received: %r", max_price)

        # Filter by low stock
        low_stock = self.request.GET.get("low_stock", "").strip()
        if low_stock:
            queryset = queryset.filter(
                stock_quantity__lt=models.F("low_stock_threshold"),
            )

        # Ordering
        sort_by = self.request.GET.get("sort_by", "-created_at")
        if sort_by in [
            "name",
            "-name",
            "price",
            "-price",
            "stock_quantity",
            "-stock_quantity",
            "created_at",
            "-created_at",
        ]:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        context = super().get_context_data(**kwargs)
        context["filter_form"] = ProductFilterForm(self.request.GET)
        context["search"] = self.request.GET.get("search", "")
        context["sort_by"] = self.request.GET.get("sort_by", "-created_at")
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Display product details."""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new product."""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")
    success_message = _("Product created successfully")

    def form_valid(self, form):
        """Set created_by to current user."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update an existing product."""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")
    success_message = _("Product updated successfully")

    def form_valid(self, form):
        """Set updated_by to current user."""
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Delete a product."""

    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("products:list")
    success_message = _("Product deleted successfully")
