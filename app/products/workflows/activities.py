import asyncio
import logging
from decimal import Decimal

from django.conf import settings
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface import HuggingFaceEndpoint
from pydantic import BaseModel
from pydantic import Field
from temporalio import activity

from app.products.constants import ProductStatus
from app.products.models import Product

logger = logging.getLogger(__name__)


class PriceSuggestion(BaseModel):
    suggested_price: float = Field(description="Optimal market price in GHS.")
    currency: str = Field(default="GHS", description="Currency abbreviation.")
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence rating from 0.0 to 1.0.",
    )
    reasoning: str = Field(description="Brief justification for the valuation.")


def suggest_market_price_with_hf(product: Product) -> PriceSuggestion:
    """Return a validated market price suggestion from Hugging Face."""
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-Coder-3B-Instruct",
        provider="nscale",
        huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
        max_new_tokens=512,
        temperature=0.1,
    )
    chat_model = ChatHuggingFace(llm=llm)
    parser = PydanticOutputParser(pydantic_object=PriceSuggestion)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert e-commerce valuation engine.\n"
                    "Return raw JSON matching this schema exactly.\n"
                    "{format_instructions}"
                ),
            ),
            (
                "human",
                (
                    "Suggest a market price for this item:\n"
                    "Name: {name}\n"
                    "Category: {category}\n"
                    "Condition: {condition}\n"
                    "Description: {description}"
                ),
            ),
        ],
    )
    chain = prompt | chat_model | parser
    return chain.invoke(
        {
            "name": product.name,
            "category": product.category.name,
            "condition": product.status,
            "description": product.description or "No description provided.",
            "format_instructions": parser.get_format_instructions(),
        },
    )


@activity.defn
async def calculate_suggested_market_price(product_id: str) -> dict:

    await asyncio.sleep(2)
    product = await Product.objects.aget(pk=product_id)
    cost = float(product.cost or Decimal("0.00"))
    fallback_price = round(cost * 1.35, 2) if cost > 0 else float(product.price)

    if settings.HUGGINGFACEHUB_API_TOKEN:
        try:
            suggestion = await asyncio.to_thread(suggest_market_price_with_hf, product)
            return {
                "suggested_price": round(suggestion.suggested_price, 2),
                "recommended_margin": "35.0",
                "currency": suggestion.currency,
                "confidence_score": suggestion.confidence_score,
                "reasoning": suggestion.reasoning,
                "source": "huggingface",
            }
        except Exception:
            logger.exception("Hugging Face price suggestion failed; using fallback")

    return {
        "suggested_price": fallback_price,
        "recommended_margin": "35.0",
        "currency": "GHS",
        "confidence_score": 0.0,
        "reasoning": "Fallback pricing based on product cost.",
        "source": "cost_fallback",
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
