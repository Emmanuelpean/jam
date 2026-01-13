"""Payment-related API routes using Stripe for subscription management."""

from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.core.oauth2 import get_current_user
from app.payments import stripe, logger, payment_router


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
        # Get or create customer and check history
        customer_id, had_previous_subscription = await get_or_create_stripe_customer(current_user, db)

        # Build checkout parameters
        checkout_params = build_checkout_params(customer_id, had_previous_subscription)

        # Create checkout session
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
