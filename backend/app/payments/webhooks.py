"""Stripe webhooks module"""

import datetime as dt

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.emails.email_service import email_service
from app.models import User
from app.payments import logger, stripe


async def process_subscription_event(
    customer_id: str,
    event_type: str,
    db: Session,
    subscription_id: str | None = None,
    trial_end: float | None = None,
) -> None:
    """Process subscription event for a given user.
    :param customer_id: Stripe customer id
    :param event_type: Stripe event type
    :param db: Database session
    :param subscription_id: Stripe subscription id
    :param trial_end: Stripe trial end"""

    user = db.query(User).filter(User.stripe_details.has(customer_id=customer_id)).first()
    logger.info(f"Received event: {event_type} for customer {customer_id}")

    # Handle subscription creation
    if event_type == "customer.subscription.created":
        user.stripe_details.subscription_id = subscription_id
        user.premium.is_active = True
        db.commit()
        logger.info(f"Subscription created: {subscription_id} for user {user.id}")

    # Handle subscription deletion by setting premium as not active
    elif event_type == "customer.subscription.deleted":
        user.premium.is_active = False
        db.commit()
        logger.info(f"Subscription deleted for user {user.id}")

    # Handle trial ending soon, send email to user
    elif event_type == "customer.subscription.trial_will_end":
        try:
            trial_end_date = dt.datetime.fromtimestamp(trial_end)
            email_service.send_trial_end_notification(user.email, trial_end_date)
            logger.info(f"Trial ending notification sent to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send trial ending email to user {user.id}: {e}")
        logger.info(f"Trial ending soon for user {user.id}")

    elif event_type in ["billing_portal.session.created", "customer.created"]:
        pass

    else:
        logger.error(f"Unhandled event type: {event_type}")

    # Update the user's subscription status'
    subscription_status = await get_subscription_status(user)
    user.stripe_details.subscription_status = subscription_status["status"]
    user.stripe_details.trial_end_date = subscription_status["trial_end"]
    db.commit()


async def get_subscription_status(current_user: User) -> dict:
    """Get subscription status and trial information for the current user.
    :param current_user: Authenticated user from JWT token
    :return: dict with subscription status and remaining trial days"""

    if not current_user.stripe_details.subscription_id:
        return {"status": None, "trial_end": None}
    try:
        subscription = await stripe.Subscription.retrieve_async(current_user.stripe_details.subscription_id)
        logger.info(f"Retrieved subscription status for user {current_user.id}. Trial end: {subscription.trial_end}")
        return {"status": subscription.status, "trial_end": subscription.trial_end}
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve subscription for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
