"""Mock webhook endpoints for testing Stripe subscription flows."""

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from core.oauth2 import get_current_user
from app.payments import logger, stripe

test_router = APIRouter(prefix="/test", tags=["testing"])


@test_router.delete("/delete-customer")
async def delete_stripe_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete the current user's Stripe customer and cancel all subscriptions.
    This permanently deletes the customer from Stripe and immediately cancels
    any active subscriptions. This action cannot be undone.
    :param current_user: Authenticated user from JWT token
    :param db: Database session
    :return: dict with deletion confirmation
    :raises HTTPException: If customer doesn't exist or Stripe error occurs"""

    try:
        # Check if user has a Stripe customer ID
        if not current_user.stripe_details.customer_id:
            raise HTTPException(status_code=404, detail="No Stripe customer found for this user")

        # Delete customer from Stripe (also cancels active subscriptions)
        deleted_customer = await stripe.Customer.delete_async(current_user.stripe_details.customer_id)

        if not deleted_customer.get("deleted"):
            raise HTTPException(status_code=500, detail="Failed to delete Stripe customer")

        logger.info(f"Deleted Stripe customer {current_user.stripe_details.customer_id} " f"for user {current_user.id}")

        # Clear Stripe customer ID from database
        current_user.stripe_details.customer_id = None
        db.commit()

        return {
            "success": True,
            "message": "Stripe customer deleted successfully",
            "customer_id": deleted_customer["id"],
        }

    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid Stripe customer {current_user.stripe_details.customer_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Stripe customer not found or already deleted")
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error deleting customer for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting customer for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")


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
                raise HTTPException(status_code=404, detail="No Stripe customer found. Create a subscription first.")

            # Retrieve customer to get their test clock
            customer = await stripe.Customer.retrieve_async(current_user.stripe_details.customer_id)
            test_clock_id = customer.get("test_clock")

            if not test_clock_id:
                raise HTTPException(status_code=404, detail="Customer is not associated with a test clock")

        # Retrieve current test clock to get frozen_time
        test_clock = await stripe.test_helpers.TestClock.retrieve_async(test_clock_id)

        if test_clock.status != "ready":
            raise HTTPException(
                status_code=409, detail=f"Test clock is currently {test_clock.status}. Wait until ready."
            )

        # Calculate new frozen time (current + days)
        current_frozen_time = test_clock.frozen_time
        seconds_to_advance = request.days * 24 * 60 * 60
        new_frozen_time = current_frozen_time + seconds_to_advance

        # Advance the test clock
        await stripe.test_helpers.TestClock.advance_async(test_clock_id, frozen_time=new_frozen_time)

        logger.info(f"Advanced test clock {test_clock_id} by {request.days} days for user {current_user.id}")

        # Wait briefly for clock to finish advancing

        await asyncio.sleep(1)

        # Retrieve updated status
        updated_clock = await stripe.test_helpers.TestClock.retrieve_async(test_clock_id)

        return {
            "success": True,
            "test_clock_id": test_clock_id,
            "days_advanced": request.days,
            "previous_time": datetime.fromtimestamp(current_frozen_time).isoformat(),
            "new_time": datetime.fromtimestamp(new_frozen_time).isoformat(),
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
