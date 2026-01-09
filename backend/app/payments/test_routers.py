"""Mock webhook endpoints for testing Stripe subscription flows."""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.model_registry import User
from app.oauth2 import get_current_user
from app.payments import logger
from app.payments.checkout import build_checkout_params
from app.payments.webhooks import handle_subscription_event

test_router = APIRouter(prefix="/test", tags=["testing"])


class MockWebhookRequest(BaseModel):
    customer_email: str
    event_type: Literal[
        "customer.subscription.created",
        "customer.subscription.deleted",
        "customer.subscription.trial_will_end",
        "customer.subscription.paused",
    ]
    subscription_id: str = "sub_test_123456789"
    customer_id: str = "cus_test_123456789"
    trial_end: int | None = None


@test_router.post("/trigger-webhook")
async def trigger_mock_webhook(
    request: MockWebhookRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Trigger webhook events for testing - bypasses signature verification."""

    # Pre-link user by email for testing (bypass Stripe API)
    user = db.query(User).filter(User.email == request.customer_email).first()
    if not user:
        return {"status": "user_not_found"}

    if not user.stripe_customer_id:
        user.stripe_customer_id = request.customer_id
        db.commit()

    subscription_data = {
        "id": request.subscription_id,
        "customer": request.customer_id,
        "trial_end": request.trial_end,
    }

    # Use shared logic but disable Stripe API calls
    return await handle_subscription_event(
        event_type=request.event_type,
        subscription_data=subscription_data,
        db=db,
        use_stripe_api=False,  # Skip Stripe API for testing
    )


@test_router.post("/create-subscription-checkout/new-user")
async def mock_checkout_new_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mock checkout for NEW USER - never had a subscription.
    - No previous subscription history
    - Gets 14-day trial
    - Payment method optional (if_required)"""

    customer_id = current_user.stripe_customer_id or f"cus_test_new_{current_user.id}"

    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = customer_id
        db.commit()

    # New user - no previous subscription
    had_previous_subscription = False
    checkout_params = build_checkout_params(customer_id, had_previous_subscription)

    trial_offered = "subscription_data" in checkout_params
    mock_client_secret = f"cs_test_new_user_{current_user.id}_trial"

    logger.info(f"Mock checkout: NEW USER {current_user.id} - trial offered")

    return {
        "clientSecret": mock_client_secret,
        "_test_info": {
            "user_type": "new_user",
            "customer_id": customer_id,
            "trial_offered": trial_offered,
            "payment_required": False,
        },
    }


@test_router.post("/create-subscription-checkout/trial-ended")
async def mock_checkout_trial_ended(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mock checkout for USER WHOSE TRIAL ENDED - subscription was canceled.

    - Had previous subscription (canceled)
    - No trial offered
    - Payment method REQUIRED (always)
    """
    customer_id = current_user.stripe_customer_id or f"cus_test_ended_{current_user.id}"

    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = customer_id
        db.commit()

    # Returning user - had previous subscription
    had_previous_subscription = True
    checkout_params = build_checkout_params(customer_id, had_previous_subscription)

    trial_offered = "subscription_data" in checkout_params
    mock_client_secret = f"cs_test_trial_ended_{current_user.id}_notrial"

    logger.info(f"Mock checkout: TRIAL ENDED {current_user.id} - payment required")

    return {
        "clientSecret": mock_client_secret,
        "_test_info": {
            "user_type": "trial_ended",
            "customer_id": customer_id,
            "trial_offered": trial_offered,
            "payment_required": True,
        },
    }


@test_router.post("/create-subscription-checkout/active-subscriber")
async def mock_checkout_active_subscriber(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mock checkout for ACTIVE SUBSCRIBER trying to subscribe again.

    - Has active subscription
    - No trial offered
    - Payment method REQUIRED (always)

    Note: In production, you might want to prevent this entirely.
    """
    customer_id = current_user.stripe_customer_id or f"cus_test_active_{current_user.id}"

    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = customer_id
        db.commit()

    # Active subscriber - definitely has previous subscription
    had_previous_subscription = True
    checkout_params = build_checkout_params(customer_id, had_previous_subscription)

    trial_offered = "subscription_data" in checkout_params
    mock_client_secret = f"cs_test_active_{current_user.id}_notrial"

    logger.info(f"Mock checkout: ACTIVE SUBSCRIBER {current_user.id} - payment required")

    return {
        "clientSecret": mock_client_secret,
        "_test_info": {
            "user_type": "active_subscriber",
            "customer_id": customer_id,
            "trial_offered": trial_offered,
            "payment_required": True,
        },
    }


@test_router.post("/create-subscription-checkout/paused-subscription")
async def mock_checkout_paused_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mock checkout for USER WITH PAUSED SUBSCRIPTION.

    - Had subscription that was paused
    - No trial offered
    - Payment method REQUIRED (always)
    """
    customer_id = current_user.stripe_customer_id or f"cus_test_paused_{current_user.id}"

    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = customer_id
        db.commit()

    # Paused subscription - has previous subscription history
    had_previous_subscription = True
    checkout_params = build_checkout_params(customer_id, had_previous_subscription)

    trial_offered = "subscription_data" in checkout_params
    mock_client_secret = f"cs_test_paused_{current_user.id}_notrial"

    logger.info(f"Mock checkout: PAUSED SUBSCRIPTION {current_user.id} - payment required")

    return {
        "clientSecret": mock_client_secret,
        "_test_info": {
            "user_type": "paused_subscription",
            "customer_id": customer_id,
            "trial_offered": trial_offered,
            "payment_required": True,
        },
    }


@test_router.post("/create-subscription-checkout/customer-no-subscription")
async def mock_checkout_customer_no_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mock checkout for EXISTING CUSTOMER who NEVER subscribed.

    - Customer exists in Stripe
    - But never created a subscription
    - Gets 14-day trial
    - Payment method optional (if_required)
    """
    customer_id = current_user.stripe_customer_id or f"cus_test_nosub_{current_user.id}"

    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = customer_id
        db.commit()

    # Customer exists but never subscribed
    had_previous_subscription = False
    checkout_params = build_checkout_params(customer_id, had_previous_subscription)

    trial_offered = "subscription_data" in checkout_params
    mock_client_secret = f"cs_test_customer_nosub_{current_user.id}_trial"

    logger.info(f"Mock checkout: CUSTOMER NO SUB {current_user.id} - trial offered")

    return {
        "clientSecret": mock_client_secret,
        "_test_info": {
            "user_type": "customer_no_subscription",
            "customer_id": customer_id,
            "trial_offered": trial_offered,
            "payment_required": False,
        },
    }
