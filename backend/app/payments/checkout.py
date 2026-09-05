"""Stripe checkout module"""

from app.config import settings
from app.payments import stripe, logger


async def build_checkout_params(customer_id: str) -> dict:
    """Build checkout session parameters based on customer history.
    :param customer_id: Stripe customer ID
    :return: Dictionary of checkout session parameters"""

    # Check if customer had any previous subscriptions (including cancelled)
    subscriptions = await stripe.Subscription.list_async(customer=customer_id, status="all", limit=1)

    checkout_params = {
        "customer": customer_id,
        "line_items": [
            {
                "price": settings.stripe_premium_price_id,
                "quantity": 1,
            }
        ],
        "mode": "subscription",
        "locale": "auto",
        "ui_mode": "hosted_page",
        "allow_promotion_codes": True,
        "success_url": f"{settings.frontend_url}/settings/premium?success=true",
        "cancel_url": f"{settings.frontend_url}/settings/premium?canceled=true",
        "subscription_data": {},
    }

    # Previous subscriber - no trial, payment required
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
