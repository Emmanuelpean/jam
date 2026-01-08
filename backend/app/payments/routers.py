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


async def handle_subscription_event(
    event_type: str,
    subscription_data: dict,
    db: Session,
) -> dict:
    """Handle subscription events.
    :param event_type: Stripe event type
    :param subscription_data: Subscription object data
    :param db: Database session
    :return: dict with status"""

    subscription_id = subscription_data.get("id")
    customer_id = subscription_data.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    # Create user link if not exists
    if not user:
        try:
            customer = await stripe.Customer.retrieve_async(customer_id)
            user = db.query(User).filter(User.email == customer.email).first()

            if not user:
                logger.error(f"No user found for email {customer.email}")
                return {"status": "user_not_found"}

            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            db.commit()
            logger.info(f"Linked customer {customer_id} to user {user.id}")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            return {"status": "error"}

    logger.info(f"Received event: {event_type} for customer {customer_id}")

    # Handle subscription creation
    if event_type == "customer.subscription.created":
        user.stripe_subscription_id = subscription_id
        user.toast_active = True
        db.commit()
        logger.info(f"Subscription created: {subscription_id} for user {user.id}")

    # Handle subscription deletion
    elif event_type == "customer.subscription.deleted":
        user.stripe_subscription_id = None
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

    # Handle subscription pause
    elif event_type == "customer.subscription.paused":
        user.toast_active = False
        db.commit()
        logger.info(f"Subscription paused for user {user.id}")

    else:
        logger.info(f"Unhandled event type: {event_type}")

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


@payment_router.post("/create-portal-session")
async def create_portal_session(
    request: SubscriptionRequest,
) -> dict:
    """Create a Stripe Customer Portal session for subscription management."""
    try:
        customers = await stripe.Customer.list_async(email=request.customer_email, limit=1)

        if not customers.data:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customers.data[0]

        # Create portal session
        portal_session = await stripe.billing_portal.Session.create_async(
            customer=customer.id,
            return_url=f"{settings.frontend_url}/settings",  # Adjust to your frontend URL
        )

        return {"url": portal_session.url}
    except Exception as e:
        logger.error(f"Failed to create portal session: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
            import time

            trial_days_remaining = max(0, int((subscription.trial_end - time.time()) / 86400))

        return {
            "status": subscription.status,
            "trial_end": subscription.trial_end,
            "trial_days_remaining": trial_days_remaining,
        }
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
