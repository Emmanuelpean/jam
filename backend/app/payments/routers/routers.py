"""Payment-related API endpoints using FastAPI and Stripe."""

import json

from fastapi import Request, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.config import settings
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models import User
from app.payments import logger, stripe
from app.payments.checkout import build_checkout_params
from app.payments.customer import get_or_create_stripe_customer
from app.payments.webhooks import process_subscription_event


payment_router = APIRouter(prefix="/payments", tags=["payments"])


@payment_router.post("/create-subscription-checkout")
async def create_subscription_checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a Stripe Customer and Checkout Session for the current user.
    New customers get a 14-day trial without a payment method required.
    Returning customers must provide a payment method upfront.
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
    )
    return {"status": "success"}


@payment_router.post("/create-portal-session")
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
            return_url=f"{settings.frontend_url}/settings/premium?success=true",
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
