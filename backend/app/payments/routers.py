"""Payment-related API endpoints using FastAPI and Stripe."""

import json
import math
import time

from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.config import settings
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models import User
from app.payments.checkout import build_checkout_params
from app.payments import payment_router, logger, stripe
from app.payments.webhooks import process_subscription_event
from app.payments.customer import get_or_create_stripe_customer


@payment_router.post("/create-subscription-checkout")
async def create_subscription_checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a Stripe Customer and Checkout Session for the current user.
    New customers get a 14-day trial without payment method required.
    Returning customers must provide payment method upfront.
    :param current_user: Authenticated user from JWT token
    :param db: Database session
    :return: dict with checkout URL
    :raises HTTPException: On Stripe or database errors"""

    try:
        customer_id = await get_or_create_stripe_customer(current_user, db)
        checkout_params = await build_checkout_params(customer_id)
        checkout_session = await stripe.checkout.Session.create_async(**checkout_params)
        logger.info(f"Created checkout session {checkout_session.id} for user {current_user.id}")
        return {"url": checkout_session.url}
    except HTTPException:  # re-raise internal HTTP exceptions
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment service temporarily unavailable. Please try again.",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating checkout for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred. Please try again.",
        )


@payment_router.post("/webhooks")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Stripe webhook events
    :param request: Incoming HTTP request
    :param db: Database session"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if settings.test_mode:
        # Just parse JSON directly in dev/test mode
        event = json.loads(payload)
        print("[Stripe Event]", event)
    else:
        # Production verification
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    obj = event["data"]["object"]
    event_type = event.get("type")

    await process_subscription_event(
        customer_id=obj.get("customer"),
        event_type=event_type,
        db=db,
        subscription_id=obj.get("id"),
        trial_end=obj.get("trial_end"),
        payment_method_id=obj.get("payment_method"),
    )
    return {"status": "success"}


@payment_router.post("/create-portal-session")  # TODO
async def create_portal_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a Stripe Customer Portal session for subscription management.
    :param current_user: Authenticated user from JWT token
    :param db: Database session
    :return: dict with portal URL
    :raises HTTPException: On customer not found or Stripe errors"""

    try:
        if not current_user.stripe_details.customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No customer found. Please subscribe first.",
            )
        # Make sure that Stripe and JAM are synced
        customer_id = await get_or_create_stripe_customer(current_user, db)

        # Create portal session
        portal_session = await stripe.billing_portal.Session.create_async(
            customer=customer_id,
            return_url=f"{settings.frontend_url}/settings/premium/?success=true",
        )

        logger.info(f"Created portal session for user {current_user.id}")

        return {"url": portal_session.url}

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error creating portal for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")


@payment_router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get subscription status and trial information for the current user.
    :param current_user: Authenticated user from JWT token
    :return: dict with subscription status and remaining trial days"""

    if not current_user.stripe_details.subscription_id:
        return {"status": None, "trial_days_remaining": None}
    try:
        subscription = await stripe.Subscription.retrieve_async(current_user.stripe_details.subscription_id)
        logger.info(
            f"Retrieved subscription status for user {current_user.id}. Remaining trial days: {subscription.trial_end}"
        )

        trial_days_remaining = None
        if subscription.trial_end:
            # Get current time - use test clock time if customer has one
            current_time = time.time()
            if current_user.stripe_details.customer_id:
                customer = await stripe.Customer.retrieve_async(current_user.stripe_details.customer_id)
                if customer.get("test_clock"):
                    test_clock = await stripe.test_helpers.TestClock.retrieve_async(customer["test_clock"])
                    current_time = test_clock.frozen_time

            # Calculate remaining days (round up so partial days count as 1)
            remaining_seconds = subscription.trial_end - current_time
            trial_days_remaining = max(0, math.ceil(remaining_seconds / 86400))

        return {"status": subscription.status, "trial_days_remaining": trial_days_remaining}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve subscription for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
