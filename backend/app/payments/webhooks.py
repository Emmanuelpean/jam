"""Payment-related API routes using Stripe for subscription management."""

import datetime as dt
import time

import stripe
from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.emails.email_service import email_service
from app.models import User
from app.payments import payment_router, logger


async def get_user_from_customer_id(
    customer_id: str,
    subscription_id: str,
    db: Session,
    use_stripe_api: bool = True,
) -> User | None:
    """Get user from customer ID, with optional Stripe API fallback.
    :param customer_id: Stripe customer ID
    :param subscription_id: Stripe subscription ID
    :param db: Database session
    :param use_stripe_api: Whether to use Stripe API for lookup (False for testing)
    :return: User object or None"""

    user = db.query(User).filter(User.stripe_details.customer_id == customer_id).first()

    if not user and use_stripe_api:
        try:
            customer = await stripe.Customer.retrieve_async(customer_id)
            user = db.query(User).filter(User.email == customer.email).first()

            if not user:
                logger.error(f"No user found for email {customer.email}")
                return None

            user.stripe_details.customer_id = customer_id
            user.stripe_details.subscription_id = subscription_id
            db.commit()
            logger.info(f"Linked customer {customer_id} to user {user.id}")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            return None

    return user


async def process_subscription_event(
    event_type: str,
    user: User,
    subscription_id: str,
    subscription_data: dict,
    db: Session,
) -> None:
    """Process subscription event for a given user.
    :param event_type: Stripe event type
    :param user: User object
    :param subscription_id: Subscription ID
    :param subscription_data: Subscription object data
    :param db: Database session"""

    logger.info(f"Received event: {event_type} for customer {user.stripe_details.customer_id}")

    if event_type == "customer.subscription.created":
        user.stripe_details.subscription_id = subscription_id
        user.toast_active = True
        db.commit()
        logger.info(f"Subscription created: {subscription_id} for user {user.id}")

    # Handle subscription deletion
    elif event_type == "customer.subscription.deleted":
        user.stripe_details.subscription_id = None
        user.toast_active = False
        db.commit()
        logger.info(f"Subscription deleted for user {user.id}")

    # Handle trial ending soon
    elif event_type == "customer.subscription.trial_will_end":
        try:
            trial_end_date = dt.datetime.fromtimestamp(subscription_data.get("trial_end"))
            email_service.send_trial_end_notification(user.email, trial_end_date)
            logger.info(f"Trial ending notification sent to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send trial ending email to user {user.id}: {e}")
        logger.info(f"Trial ending soon for user {user.id}")

    else:
        logger.info(f"Unhandled event type: {event_type}")


async def handle_subscription_event(
    event_type: str,
    subscription_data: dict,
    db: Session,
    use_stripe_api: bool = True,
) -> dict:
    """Handle subscription events.
    :param event_type: Stripe event type
    :param subscription_data: Subscription object data
    :param db: Database session
    :param use_stripe_api: Whether to use Stripe API (False for testing)
    :return: dict with status"""

    subscription_id = subscription_data.get("id")
    customer_id = subscription_data.get("customer")

    user = await get_user_from_customer_id(customer_id, subscription_id, db, use_stripe_api)

    if not user:
        return {"status": "user_not_found"}

    await process_subscription_event(event_type, user, subscription_id, subscription_data, db)

    return {"status": "success"}


@payment_router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Stripe webhook events - signature verification only."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Delegate to shared business logic
    return await handle_subscription_event(
        event_type=event.type,
        subscription_data=event.data.object,
        db=db,
    )


@payment_router.get("/subscription-status/{subscription_id}")
async def get_subscription_status(
    subscription_id: str,
) -> dict:
    """Get subscription status and trial information.
    :param subscription_id: Stripe subscription ID
    :return: dict with subscription status and trial info"""

    try:
        subscription = await stripe.Subscription.retrieve_async(subscription_id)

        trial_days_remaining = None
        if subscription.status == "trialing" and subscription.trial_end:
            trial_days_remaining = max(0, int((subscription.trial_end - time.time()) / 86400))

        return {
            "status": subscription.status,
            "trial_end": subscription.trial_end,
            "trial_days_remaining": trial_days_remaining,
        }
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
