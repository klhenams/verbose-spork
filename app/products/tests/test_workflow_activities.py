from decimal import Decimal
from unittest.mock import patch

import pytest
from asgiref.sync import async_to_sync
from django.test import override_settings

from app.products.tests import ProductFactory
from app.products.workflows.activities import PriceSuggestion
from app.products.workflows.activities import calculate_suggested_market_price


@pytest.mark.django_db
def test_price_activity_uses_cost_fallback_without_hugging_face_token():
    product = ProductFactory(cost=Decimal("100.00"), price=Decimal("120.00"))

    with override_settings(HUGGINGFACEHUB_API_TOKEN=""):
        result = async_to_sync(calculate_suggested_market_price)(str(product.pk))

    assert result["suggested_price"] == 135.0  # noqa: PLR2004
    assert result["source"] == "cost_fallback"


@pytest.mark.django_db
def test_price_activity_preserves_existing_flow_with_hugging_face_price():
    product = ProductFactory()
    suggestion = PriceSuggestion(
        suggested_price=149.995,
        confidence_score=0.9,
        reasoning="Comparable products support this price.",
    )

    with (
        override_settings(HUGGINGFACEHUB_API_TOKEN="test-token"),  # noqa: S106
        patch(
            "app.products.workflows.activities.suggest_market_price_with_hf",
            return_value=suggestion,
        ),
    ):
        result = async_to_sync(calculate_suggested_market_price)(str(product.pk))

    assert result["suggested_price"] == 150.0  # noqa: PLR2004
    assert result["confidence_score"] == 0.9  # noqa: PLR2004
    assert result["source"] == "huggingface"
