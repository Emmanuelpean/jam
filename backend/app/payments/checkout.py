"""Payment-related API routes using Stripe for subscription management."""

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.payments import stripe, logger


def build_checkout_params(
    customer_id: str,
    had_previous_subscription: bool,
) -> dict:
    """Build checkout session parameters based on customer history.
    :param customer_id: Stripe customer ID
    :param had_previous_subscription: Whether customer had previous subscriptions
    :return: Dictionary of checkout session parameters"""

    checkout_params = {
        "customer": customer_id,
        "line_items": [
            {
                "price": settings.stripe_toast_price_id,
                "quantity": 1,
            }
        ],
        "mode": "subscription",
        "locale": "auto",
        "ui_mode": "embedded",
        "allow_promotion_codes": True,
        "redirect_on_completion": "never",
        "subscription_data": {},
    }

    # Configure based on customer history
    if had_previous_subscription:
        # Returning customer - no trial, payment required
        checkout_params["payment_method_collection"] = "always"
        logger.info(f"No trial for returning customer {customer_id} - payment required")
    else:
        # New customer - 14-day trial, payment optional
        checkout_params["payment_method_collection"] = "if_required"
        checkout_params["subscription_data"] = {
            "trial_period_days": 14,
            "trial_settings": {
                "end_behavior": {
                    "missing_payment_method": "cancel",
                },
            },
        }
        logger.info(f"Offering 14-day trial to new customer {customer_id}")

    return checkout_params


async def get_or_create_stripe_customer(
    user: User,
    db: Session,
) -> tuple[str, bool]:
    """Get or create Stripe customer for user.
    :param user: User object
    :param db: Database session
    :return: Tuple of (customer_id, had_previous_subscription)
    :raises HTTPException: On validation or Stripe errors"""

    try:
        # Create or get Stripe customer
        customers = await stripe.Customer.list_async(email=user.email, limit=1)

        # If customer exists...
        if customers.data:
            customer = customers.data[0]
            logger.info(f"Retrieved existing customer: {customer.email}")

            # Link customer ID to user if not already linked
            if not user.stripe_details.customer_id:
                user.stripe_details.customer_id = customer.id
                db.commit()
                logger.info(f"Linked Stripe customer {customer.id} to user {user.id}")

            # Verify customer ID matches
            if user.stripe_details.customer_id != customer.id:
                logger.warning(
                    f"Stripe customer ID mismatch for user {user.id}: "
                    f"expected {user.stripe_customer_id}, got {customer.id}"
                )
                raise HTTPException(status_code=400, detail="Customer verification failed. Please contact support.")

            # Verify email
            if customer.email != user.email:
                logger.warning(
                    f"Email mismatch for user {user.id}: " f"user email {user.email}, customer email {customer.email}"
                )
                raise HTTPException(status_code=400, detail="Customer verification failed. Please contact support.")

            # Verify metadata
            if "user_id" not in customer.metadata or customer.metadata["user_id"] != str(user.id):
                logger.warning(
                    f"Metadata mismatch for user {user.id}: "
                    f"expected user_id {user.id}, got {customer.metadata.get('user_id')}"
                )
                raise HTTPException(status_code=400, detail="Customer verification failed. Please contact support.")

        # If no customer, create one
        else:
            customer = await stripe.Customer.create_async(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )
            user.stripe_details.customer_id = customer.id
            db.commit()
            logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        # Check if customer had any paid/completed subscriptions
        subscriptions = await stripe.Subscription.list_async(customer=customer.id, limit=100)

        # Only count subscriptions that were actually paid or active
        had_previous_subscription = any(
            sub.status in ["active", "canceled", "past_due", "unpaid"] for sub in subscriptions.data
        )

        return customer.id, had_previous_subscription

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except SQLAlchemyError as e:
        logger.error(f"Database error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
