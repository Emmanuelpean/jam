"""Payment-related API routes using Stripe for subscription management."""

import datetime as dt

import stripe
from fastapi import HTTPException, Request, APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.emails.email_service import email_service
from app.model_registry import User
from app.utils import AppLogger


class SubscriptionRequest(BaseModel):
    customer_email: str


payment_router = APIRouter(prefix="/payments", tags=["payments"])
stripe.api_key = settings.stripe_secret_key
logger = AppLogger.get_logger("Stripe")


@payment_router.post("/create-subscription-checkout")
async def create_subscription_checkout(
    request: SubscriptionRequest,
) -> dict:
    """Create a Stripe Checkout Session for a monthly subscription.
    :param request: SubscriptionRequest
    :return: dict with checkout URL"""

    try:
        # Create or get customer
        customers = await stripe.Customer.list_async(email=request.customer_email, limit=1)
        if customers.data:
            customer = customers.data[0]
            logger.info(f"Retrieved customer: {customer.email}")
        else:
            customer = await stripe.Customer.create_async(email=request.customer_email)
            logger.info(f"Created customer {customer.email}")

        # Create checkout session for monthly subscription
        checkout_session = await stripe.checkout.Session.create_async(
            customer=customer.id,
            line_items=[
                {
                    "price": settings.stripe_toast_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            locale="auto",
            ui_mode="embedded",
            allow_promotion_codes=True,
            redirect_on_completion="never",
            payment_method_collection="if_required",
            subscription_data={
                "trial_period_days": 14,
                "trial_settings": {
                    "end_behavior": {
                        "missing_payment_method": "cancel",
                    },
                },
            },
        )

        return {"clientSecret": checkout_session.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Stripe webhook events for subscription management.
    :param request: Request
    :param db: Database session
    :return: dict with status"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    subscription = event.data.object
    subscription_id = subscription.id
    customer_id = subscription.customer

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    # Create user link if not exists
    if not user:
        try:
            customer = await stripe.Customer.retrieve_async(customer_id)
            user = db.query(User).filter(User.email == customer.email).first()

            if not user:
                logger.error(f"No user found for email {customer.email}")
                return {"status": "user_not_found"}

            # Link customer and subscription to user
            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            db.commit()  # Commit the link here
            logger.info(f"Linked customer {customer_id} to user {user.id}")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            return {"status": "error"}

    logger.info(f"Received webhook event: {event.type} for customer {customer_id}")

    # Handle subscription creation
    if event.type == "customer.subscription.created":
        # Update subscription ID for existing customer
        user.stripe_subscription_id = subscription_id
        # Grant premium access
        user.toast_active = True
        db.commit()
        logger.info(f"Subscription created: {subscription_id} for user {user.id}")

    # Handle subscription deletion
    elif event.type == "customer.subscription.deleted":
        user.stripe_subscription_id = None
        user.toast_active = False
        db.commit()
        logger.info(f"Subscription deleted for user {user.id}")

    # Handle trial ending soon (3 days before)
    elif event.type == "customer.subscription.trial_will_end":
        try:
            trial_end_date = dt.datetime.fromtimestamp(subscription.trial_end)
            email_service.send_trial_end_notification(user.email, trial_end_date)
            logger.info(f"Trial ending notification sent to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send trial ending email to user {user.id}: {e}")
        logger.info(f"Trial ending soon for user {user.id}, trial_end: {subscription.trial_end}")

    # Handle subscription pause (e.g., trial ended without payment)
    elif event.type == "customer.subscription.paused":
        user.toast_active = False
        db.commit()
        logger.info(f"Subscription paused for user {user.id}")

    # Handle the rest
    else:
        logger.info(f"Unhandled event type: {event.type}")

    return {"status": "success"}


# @payment_router.get("/is-trial-over/{subscription_id}")
# async def is_trial_over(
#     current_user=Depends(oauth2.get_current_user),
# ) -> bool:
#     """Check if subscription trial has ended."""
#
#     if not current_user.stripe_subscription_id:
#         return True
#
#     subscription = await stripe.Subscription.retrieve_async(current_user.stripe_subscription_id)
#
#     if subscription.status == "trialing":
#         return False
#
#     if subscription.trial_end:
#         import time
#
#         return subscription.trial_end < time.time()
#
#     return True
