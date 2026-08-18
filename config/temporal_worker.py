import asyncio
import logging
import os

import django
from temporalio.client import Client
from temporalio.worker import Worker

from app.products.workflows.activities import calculate_suggested_market_price
from app.products.workflows.activities import publish_product
from app.products.workflows.activities import revert_product_status
from app.products.workflows.activities import update_product_price
from app.products.workflows.workflows import ProductPriceOnboardingWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()


async def main() -> None:
    temporal_host = os.environ.get("TEMPORAL_HOST", "temporal:7233")
    logger.info("Connecting Temporal worker to %s...", temporal_host)

    client = await Client.connect(temporal_host)

    worker = Worker(
        client,
        task_queue="product-tasks",
        workflows=[
            ProductPriceOnboardingWorkflow,
        ],
        activities=[
            calculate_suggested_market_price,
            update_product_price,
            publish_product,
            revert_product_status,  # Registered compensation activity
        ],
    )

    logger.info("Worker started on task queue 'product-tasks'. Awaiting jobs...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
