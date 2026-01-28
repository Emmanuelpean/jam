"""Stripe checkout module"""

from app.config import settings
from app.models import User
from app.payments import stripe, logger


async def build_checkout_params(
    current_user: User,
    customer_id: str,
) -> dict:
    """Build checkout session parameters based on customer history.
    :param current_user: Current user object
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
        "ui_mode": "hosted",
        "allow_promotion_codes": True,
        "success_url": f"{settings.frontend_url}/settings/premium?success=true",
        "cancel_url": f"{settings.frontend_url}/settings/premium?canceled=true",
        "subscription_data": {},
    }

    # Previous customer - no trial, payment required
    if subscriptions.data:
        logger.info(str(subscriptions.data))
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
