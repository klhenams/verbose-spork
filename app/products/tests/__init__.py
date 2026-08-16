"""Test factories for products app."""

import factory
from factory.django import DjangoModelFactory

from app.products.constants import ProductStatus
from app.products.models import Category
from app.products.models import Product
from app.users.tests.factories import UserFactory


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances."""

    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("text")

    class Meta:
        model = Category


class ProductFactory(DjangoModelFactory):
    """Factory for creating Product instances."""

    name = factory.Faker("word")
    description = factory.Faker("text")
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    cost = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    stock_quantity = factory.Faker("random_int", min=0, max=1000)
    low_stock_threshold = factory.Faker("random_int", min=5, max=50)
    category = factory.SubFactory(CategoryFactory)
    status = ProductStatus.ACTIVE
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Product
