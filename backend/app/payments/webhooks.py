"""Stripe webhooks module"""

import datetime as dt

from sqlalchemy.orm import Session

from app.emails.email_service import email_service
from app.models import User
from app.payments import logger, stripe


async def process_subscription_event(
    customer_id: str,
    event_type: str,
    db: Session,
    subscription_id: str | None = None,
    trial_end: float | None = None,
    payment_method_id: str | None = None,
) -> None:
    """Process subscription event for a given user.
    :param customer_id: Stripe customer id
    :param event_type: Stripe event type
    :param db: Database session
    :param subscription_id: Stripe subscription id
    :param trial_end: Stripe trial end
    :param payment_method_id: Stripe payment method id"""

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

    # # Handle payment method added via portal
    # elif event_type == "setup_intent.succeeded":
    #     if customer_id and payment_method_id:
    #         # Set as customer's default payment method
    #         await stripe.Customer.modify_async(
    #             customer_id,
    #             invoice_settings={"default_payment_method": payment_method_id},
    #         )
    #
    #         # Update active and trialing subscriptions to use this payment method
    #         for sub_status in ["active", "trialing"]:
    #             subscriptions = await stripe.Subscription.list_async(customer=customer_id, status=sub_status)
    #             for sub in subscriptions.data:
    #                 await stripe.Subscription.modify_async(sub.id, default_payment_method=payment_method_id)
    #
    #         logger.info(f"Set default payment method {payment_method_id} for customer {customer_id}")

    elif event_type in ["billing_portal.session.created", "customer.created"]:
        pass

    else:
        logger.error(f"Unhandled event type: {event_type}")
