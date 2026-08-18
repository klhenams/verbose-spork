import asyncio
from decimal import Decimal

from temporalio import activity

from app.products.constants import ProductStatus
from app.products.models import Product


@activity.defn
async def calculate_suggested_market_price(product_id: str) -> dict:

    # Simulate external API analysis delay
    await asyncio.sleep(2)
    product = await Product.objects.aget(pk=product_id)
    cost = float(product.cost or Decimal("0.00"))
    suggested_price = round(cost * 1.35, 2) if cost > 0 else float(product.price)

    return {
        "suggested_price": suggested_price,
        "recommended_margin": "35.0",
    }


@activity.defn
async def update_product_price(params: dict) -> None:

    product = await Product.objects.aget(pk=params["product_id"])
    product.price = Decimal(str(params["final_price"]))
    await product.asave(update_fields=["price", "updated_at"])


@activity.defn
async def publish_product(params: dict) -> None:

    if params.get("should_fail"):
        msg = "Simulated External Search Indexing / Marketplace Sync Error!"
        raise RuntimeError(msg)

    product = await Product.objects.aget(pk=params["product_id"])
    product.status = ProductStatus.ACTIVE
    await product.asave(update_fields=["status", "updated_at"])


@activity.defn
async def revert_product_status(params: dict) -> None:

    product = await Product.objects.aget(pk=params["product_id"])
    product.status = ProductStatus.FAILED_PUBLISH
    await product.asave(update_fields=["status", "updated_at"])
