from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Category
from .models import Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Category name"),
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Category description"),
                },
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "sku",
            "price",
            "cost",
            "stock_quantity",
            "low_stock_threshold",
            "category",
            "status",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Product name"),
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Product description"),
                },
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Stock keeping unit"),
                },
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": _("Selling price"),
                },
            ),
            "cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": _("Cost price"),
                },
            ),
            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": _("Current stock"),
                },
            ),
            "low_stock_threshold": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": _("Low stock alert level"),
                },
            ),
            "category": forms.Select(
                attrs={"class": "form-control"},
            ),
            "status": forms.Select(
                attrs={"class": "form-control"},
            ),
        }


class ProductFilterForm(forms.Form):
    """Form for filtering products."""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Search by name or SKU"),
            },
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        choices=[("", _("All Statuses")), *Product.STATUS_CHOICES],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Min price"),
                "step": "0.01",
            },
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Max price"),
                "step": "0.01",
            },
        ),
    )
