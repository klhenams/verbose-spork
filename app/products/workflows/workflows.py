from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from app.products.workflows.activities import calculate_suggested_market_price
    from app.products.workflows.activities import publish_product
    from app.products.workflows.activities import revert_product_status
    from app.products.workflows.activities import update_product_price


@workflow.defn
class ProductPriceOnboardingWorkflow:
    def __init__(self) -> None:
        self.suggested_pricing: dict | None = None
        self.selected_price: float | None = None
        self.is_approved: bool = False

    @workflow.signal
    def approve_suggested_price(self, chosen_price: float) -> None:
        self.selected_price = chosen_price
        self.is_approved = True

    @workflow.query
    def get_pricing_recommendation(self) -> dict | None:
        return self.suggested_pricing

    @workflow.run
    async def run(self, input_data: dict) -> dict:
        product_id = str(input_data["product_id"])
        # Short timeout override for testing Case 2 (e.g. 20s instead of 24h)
        timeout_seconds = input_data.get("timeout_seconds", 86400)
        should_fail_publish = input_data.get("should_fail_publish", False)

        # Task 2: Calculate Market Price
        self.suggested_pricing = await workflow.execute_activity(
            calculate_suggested_market_price,
            product_id,
            start_to_close_timeout=timedelta(seconds=15),
        )

        # VISUAL DELAY FOR TEMPORAL UI: Pause for 10 seconds to inspect state
        await workflow.sleep(timedelta(seconds=10))

        # Human Approval Wait (or Timeout)
        try:
            await workflow.wait_condition(
                lambda: self.is_approved,
                timeout=timedelta(seconds=timeout_seconds),
            )
        except TimeoutError:
            self.selected_price = self.suggested_pricing["suggested_price"]

        # Task 3: Update Price Activity
        await workflow.execute_activity(
            update_product_price,
            {
                "product_id": product_id,
                "final_price": self.selected_price,
            },
            start_to_close_timeout=timedelta(seconds=10),
        )

        # VISUAL DELAY: Pause 5 seconds before publishing
        await workflow.sleep(timedelta(seconds=5))

        # Task 4: Publish Product with Retry Policy
        try:
            await workflow.execute_activity(
                publish_product,
                {
                    "product_id": product_id,
                    "should_fail": should_fail_publish,
                },
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=2),
                    backoff_coefficient=2.0,
                ),
            )
        except ActivityError as err:
            # Saga Compensation Handler
            await workflow.execute_activity(
                revert_product_status,
                {
                    "product_id": product_id,
                    "reason": str(err),
                },
                start_to_close_timeout=timedelta(seconds=10),
            )
            return {
                "status": "FAILED_PUBLISH",
                "final_price": self.selected_price,
                "error": "Publishing failed. Status reverted via Saga.",
            }

        return {
            "status": "PUBLISHED",
            "final_price": self.selected_price,
            "was_auto_approved": not self.is_approved,
        }
