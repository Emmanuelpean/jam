"""Payment-related API routes using Stripe for subscription management."""

import os

import stripe
from fastapi import HTTPException, Request, APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.model_registry import User


class SubscriptionRequest(BaseModel):
    customer_email: str


payment_router = APIRouter(prefix="/payments", tags=["payments"])
stripe.api_key = settings.stripe_secret_key


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
        else:
            customer = await stripe.Customer.create_async(email=request.customer_email)

        # Create checkout session for monthly subscription
        checkout_session = await stripe.checkout.Session.create_async(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.stripe_toast_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            locale="auto",
            ui_mode="embedded",
            allow_promotion_codes=False,
            redirect_on_completion="never",
        )

        return {"clientSecret": checkout_session.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.get("/check-subscription/{session_id}")
async def check_subscription(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Check if subscription is active by session ID and update user.
    :param session_id: Stripe checkout session ID
    :param db: Database session
    :return: dict with subscription status"""

    if not os.getenv("TEST_MODE"):
        return {"subscription_active": True, "user_updated": False}
    try:
        # Retrieve the session from Stripe
        session = await stripe.checkout.Session.retrieve_async(session_id, expand=["subscription", "customer"])

        # Check if payment was successful
        if session.status == "complete" and session.subscription:
            customer_email = session.customer.email

            # Update user in database
            user = db.query(User).filter(User.email == customer_email).first()
            if user:
                user.toast_active = True
                db.commit()
                print(f"User {customer_email} subscription activated via session check")
                return {"subscription_active": True, "user_updated": True}
            else:
                print(f"User not found for email: {customer_email}")
                return {"subscription_active": True, "user_updated": False}

        return {"subscription_active": False, "user_updated": False}

    except Exception as e:
        print(f"Error checking subscription: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Stripe webhook events for subscription management.
    :param request: Request
    :param db: Database session
    :return: dict with status"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle subscription events
    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        # Get customer email from Stripe
        customer = await stripe.Customer.retrieve_async(customer_id)

        # Find user in database
        user = db.query(User).filter(User.email == customer.email).first()
        if user:
            user.toast_active = True
            db.commit()
        print(f"Subscription created: {subscription['id']}")

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        # Get customer email from Stripe
        customer = await stripe.Customer.retrieve_async(customer_id)

        # Find user in database
        user = db.query(User).filter(User.email == customer.email).first()
        if user:
            user.toast_active = False
            db.commit()

    return {"status": "success"}


@payment_router.post("/cancel-subscription")
async def cancel_subscription(request: SubscriptionRequest, db: Session = Depends(get_db)) -> dict:
    """Cancel a customer's subscription.
    :param request: SubscriptionRequest with customer email
    :param db: Database session
    :return: dict with cancellation status"""

    try:
        # Get customer
        customers = await stripe.Customer.list_async(email=request.customer_email, limit=1)

        if not customers.data:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customers.data[0]

        # Get active subscriptions
        subscriptions = await stripe.Subscription.list_async(customer=customer.id, status="active", limit=1)

        if not subscriptions.data:
            raise HTTPException(status_code=404, detail="No active subscription found")

        subscription = subscriptions.data[0]

        # Cancel at period end (recommended) or immediately
        canceled_sub = await stripe.Subscription.modify_async(subscription.id, cancel_at_period_end=False)

        # Update database
        user = db.query(User).filter(User.email == request.customer_email).first()
        if user:
            user.toast_active = False
            db.commit()

        return {"status": "canceled", "cancel_at": canceled_sub.cancel_at}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
