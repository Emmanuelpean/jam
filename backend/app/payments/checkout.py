"""Payment-related API routes using Stripe for subscription management."""

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.payments import stripe, logger


async def build_checkout_params(customer_id: str) -> dict:
    """Build checkout session parameters based on customer history.
    :param customer_id: Stripe customer ID
    :return: Dictionary of checkout session parameters"""

    # Check if customer had any paid/completed subscriptions
    subscriptions = await stripe.Subscription.list_async(customer=customer_id, limit=100)

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

    # Previous customer - no trial, payment required
    if subscriptions.data:
        checkout_params["payment_method_collection"] = "always"
        logger.info(f"No trial for returning customer {customer_id} - payment required")

    # New customer - 14-day trial, payment optional
    else:
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
) -> str:
    """Get or create Stripe customer for the user.
    :param user: User object
    :param db: Database session
    :return: Customer ID string
    :raises HTTPException: On validation or Stripe errors"""

    try:
        # Retrieve the existing customer
        if user.stripe_details.customer_id:
            customer = await stripe.Customer.retrieve_async(user.stripe_details.customer_id)

            # Update Stripe email if it doesn't match our database
            if customer.email != user.email:
                customer = await stripe.Customer.modify_async(user.stripe_details.customer_id, email=user.email)
                logger.info(f"Updated Stripe customer {customer.id} email to {user.email}")
            else:
                logger.info(f"Retrieved existing Stripe customer {customer.id} for user {user.id}")

        # If no customer, create one
        else:
            customer = await stripe.Customer.create_async(email=user.email, metadata={"user_id": str(user.id)})
            user.stripe_details.customer_id = customer.id
            db.commit()
            logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        return user.stripe_details.customer_id

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except SQLAlchemyError as e:
        logger.error(f"Database error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
