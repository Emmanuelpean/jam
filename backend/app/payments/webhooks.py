"""Stripe webhooks module"""

import datetime as dt

from sqlalchemy.orm import Session

from app.emails.email_service import email_service
from app.models import User
from app.payments import logger


def process_subscription_event(
    customer_id: str,
    subscription_id: str,
    event_type: str,
    trial_end: float | None,
    db: Session,
) -> None:
    """Process subscription event for a given user.
    :param subscription_id: Stripe subscription id
    :param customer_id: Stripe customer id
    :param event_type: Stripe event type
    :param trial_end: Stripe trial end
    :param db: Database session"""

    user = db.query(User).filter(User.stripe_details.has(customer_id=customer_id)).first()
    logger.info(f"Received event: {event_type} for customer {customer_id}")

    # Handle subscription creation
    if event_type == "customer.subscription.created":
        user.stripe_details.subscription_id = subscription_id
        user.premium.is_active = True
        db.commit()
        logger.info(f"Subscription created: {subscription_id} for user {user.id}")

    # Handle subscription deletion
    elif event_type == "customer.subscription.deleted":
        user.stripe_details.subscription_id = None
        user.premium.is_active = False
        db.commit()
        logger.info(f"Subscription deleted for user {user.id}")

    # Handle trial ending soon
    elif event_type == "customer.subscription.trial_will_end":
        try:
            trial_end_date = dt.datetime.fromtimestamp(trial_end)
            email_service.send_trial_end_notification(user.email, trial_end_date)
            logger.info(f"Trial ending notification sent to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send trial ending email to user {user.id}: {e}")
        logger.info(f"Trial ending soon for user {user.id}")

    else:
        logger.error(f"Unhandled event type: {event_type}")
