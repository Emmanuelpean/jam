"""Mock webhook endpoints for testing Stripe subscription flows."""

import asyncio
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status

from app.core.oauth2 import get_current_user
from app.models import User
from app.payments import logger, stripe

test_router = APIRouter(prefix="/test", tags=["testing"])


@test_router.delete("/delete-all-customers")
async def delete_all_stripe_customers() -> dict:
    """Delete ALL Stripe customers, test clocks, and cancel all subscriptions.
    WARNING: This permanently deletes ALL customers and test clocks from Stripe
    and immediately cancels all active subscriptions across your entire account.
    This action cannot be undone.
    :return: dict with deletion summary"""

    deleted_customers = 0
    deleted_clocks = 0
    failed_deletions = []

    try:
        # Delete all customers with pagination
        has_more = True
        starting_after = None

        while has_more:
            params = {"limit": 100}
            if starting_after:
                params["starting_after"] = starting_after  # noqa

            customers = await stripe.Customer.list_async(**params)

            for customer in customers.data:
                try:
                    deleted_customer = await stripe.Customer.delete_async(customer.id)
                    if deleted_customer.get("deleted"):
                        deleted_customers += 1
                        logger.info(f"Deleted Stripe customer {customer.id}")
                    else:
                        failed_deletions.append(customer.id)
                except stripe.error.StripeError as e:
                    logger.error(f"Failed to delete customer {customer.id}: {str(e)}")
                    failed_deletions.append(customer.id)

            has_more = customers.has_more
            if has_more and customers.data:
                starting_after = customers.data[-1].id

        # Delete all test clocks with pagination
        has_more = True
        starting_after = None

        while has_more:
            params = {"limit": 100}
            if starting_after:
                params["starting_after"] = starting_after  # noqa

            test_clocks = await stripe.test_helpers.TestClock.list_async(**params)

            for clock in test_clocks.data:
                try:
                    await stripe.test_helpers.TestClock.delete_async(clock.id)
                    deleted_clocks += 1
                    logger.info(f"Deleted test clock {clock.id}")
                except stripe.error.StripeError as e:
                    logger.error(f"Failed to delete test clock {clock.id}: {str(e)}")
                    failed_deletions.append(clock.id)

            has_more = test_clocks.has_more
            if has_more and test_clocks.data:
                starting_after = test_clocks.data[-1].id

        return {
            "success": True,
            "message": f"Deleted {deleted_customers} customers and {deleted_clocks} test clocks",
            "deleted_customers": deleted_customers,
            "deleted_clocks": deleted_clocks,
            "failed_count": len(failed_deletions),
            "failed_ids": failed_deletions if failed_deletions else None,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during bulk deletion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service error. Please try again.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during bulk deletion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during deletion.",
        )


class AdvanceClockRequest(BaseModel):
    days: int = Field(gt=0, le=730, description="Number of days to advance (1-730)")
    test_clock_id: str | None = Field(
        None, description="Optional test clock ID. If not provided, uses user's test clock"
    )


@test_router.post("/advance-test-clock")
async def advance_test_clock(
    request: AdvanceClockRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Advance a Stripe test clock by X days for testing subscriptions.
    This allows you to simulate time passing to test trial expirations,
    billing cycles, and subscription renewals without waiting.
    :param request: Request with days to advance and optional test_clock_id
    :param current_user: Authenticated user from JWT token
    :return: dict with updated test clock information
    :raises HTTPException: If test clock doesn't exist or Stripe error occurs"""

    try:
        # Get test clock ID (from request or retrieve user's test clock)
        test_clock_id = request.test_clock_id

        if not test_clock_id:
            # If no clock ID provided, find the user's customer test clock
            if not current_user.stripe_details.customer_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Stripe customer found. Create a subscription first.",
                )

            # Retrieve customer to get their test clock
            customer = await stripe.Customer.retrieve_async(current_user.stripe_details.customer_id)
            test_clock_id = customer.get("test_clock")

            if not test_clock_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer is not associated with a test clock",
                )

        # Retrieve current test clock to get frozen_time
        test_clock = await stripe.test_helpers.TestClock.retrieve_async(test_clock_id)

        if test_clock.status != "ready":
            raise HTTPException(
                status_code=409,
                detail=f"Test clock is currently {test_clock.status}. Wait until ready.",
            )

        # Calculate new frozen time (current + days)
        current_frozen_time = test_clock.frozen_time
        seconds_to_advance = request.days * 24 * 60 * 60
        new_frozen_time = current_frozen_time + seconds_to_advance

        # Advance the test clock
        await stripe.test_helpers.TestClock.advance_async(test_clock_id, frozen_time=new_frozen_time)

        logger.info(f"Advanced test clock {test_clock_id} by {request.days} days for user {current_user.id}")

        # Wait for the test clock to be ready again (poll up to 30 seconds)
        max_wait_time = 30
        poll_interval = 0.5
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval

            updated_clock = await stripe.test_helpers.TestClock.retrieve_async(test_clock_id)
            if updated_clock.status == "ready":
                break
        else:
            # Timeout waiting for clock to be ready
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=f"Test clock did not become ready within {max_wait_time} seconds",
            )

        # Retrieve final status
        updated_clock = await stripe.test_helpers.TestClock.retrieve_async(test_clock_id)

        return {
            "success": True,
            "test_clock_id": test_clock_id,
            "days_advanced": request.days,
            "previous_time": dt.datetime.fromtimestamp(current_frozen_time).isoformat(),
            "new_time": dt.datetime.fromtimestamp(new_frozen_time).isoformat(),
            "status": updated_clock.status,
            "message": f"Advanced test clock by {request.days} days",
        }

    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid test clock request: {str(e)}")
        raise HTTPException(status_code=404, detail="Test clock not found or invalid advancement")
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error advancing test clock: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error advancing test clock: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
