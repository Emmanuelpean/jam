"""Payment-related API endpoints using FastAPI and Stripe."""

import stripe
from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models import User
from app.payments import payment_router, logger
from app.payments import checkout
from app.payments.webhooks import process_subscription_event


@payment_router.post("/create-subscription-checkout")
async def create_subscription_checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a Stripe Checkout Session for a monthly subscription.
    New customers get a 14-day trial without payment method required.
    Returning customers must provide payment method upfront.
    :param current_user: Authenticated user from JWT token
    :param db: Database session
    :return: dict with checkout client secret
    :raises HTTPException: On Stripe or database errors"""

    try:
        customer_id = await checkout.get_or_create_stripe_customer(current_user, db)
        checkout_params = await checkout.build_checkout_params(customer_id)
        checkout_session = await stripe.checkout.Session.create_async(**checkout_params)
        logger.info(f"Created checkout session {checkout_session.id} for user {current_user.id}")
        return {"clientSecret": checkout_session.client_secret}
    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error creating checkout for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")


@payment_router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Stripe webhook events
    :param request: Incoming HTTP request
    :param db: Database session"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Delegate to shared business logic
    process_subscription_event(event.type, event.data.object, db)
    return {"status": "success"}


@payment_router.post("/create-portal-session")
async def create_portal_session(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a Stripe Customer Portal session for subscription management.
    :param current_user: Authenticated user from JWT token
    :return: dict with portal URL
    :raises HTTPException: On customer not found or Stripe errors"""

    try:
        user_email = current_user.email
        customers = await stripe.Customer.list_async(email=user_email, limit=1)

        if not customers.data:
            logger.warning(f"No Stripe customer found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="No subscription found. Please subscribe first.")

        customer = customers.data[0]

        # Create portal session
        portal_session = await stripe.billing_portal.Session.create_async(
            customer=customer.id,
            return_url=f"{settings.frontend_url}/settings/premium",
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


@payment_router.get("/subscription-status/{subscription_id}")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get subscription status and trial information.
    :param current_user: Authenticated user from JWT token
    :return: dict with subscription status and trial info"""

    try:
        return await stripe.Subscription.retrieve_async(current_user.stripe_details.customer_id)
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve subscription {current_user.stripe_details.customer_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
