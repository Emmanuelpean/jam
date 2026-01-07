"""Mock webhook endpoints for testing Stripe subscription flows."""

import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.model_registry import User
from app.utils import AppLogger

test_router = APIRouter(prefix="/test", tags=["testing"])
logger = AppLogger.get_logger("TestWebhooks")


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
    """Trigger mock Stripe webhook events for testing.

    :param request: MockWebhookRequest with event details
    :param db: Database session
    :return: dict with status and user state
    """
    user = db.query(User).filter(User.email == request.customer_email).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {request.customer_email}")

    # Link customer if not already linked
    if not user.stripe_customer_id:
        user.stripe_customer_id = request.customer_id
        user.stripe_subscription_id = request.subscription_id
        db.commit()
        logger.info(f"Linked mock customer {request.customer_id} to user {user.id}")

    logger.info(f"Mock webhook event: {request.event_type} for user {user.email}")

    # Handle subscription creation
    if request.event_type == "customer.subscription.created":
        user.stripe_subscription_id = request.subscription_id
        user.toast_active = True
        db.commit()
        logger.info(f"Mock subscription created for user {user.id}")

    # Handle subscription deletion
    elif request.event_type == "customer.subscription.deleted":
        user.stripe_subscription_id = None
        user.toast_active = False
        db.commit()
        logger.info(f"Mock subscription deleted for user {user.id}")

    # Handle trial ending soon
    elif request.event_type == "customer.subscription.trial_will_end":
        trial_end = request.trial_end or int(time.time()) + (3 * 24 * 60 * 60)
        logger.info(f"Mock trial ending for user {user.id}, trial_end: {trial_end}")
        # Email notification would be triggered here in production

    # Handle subscription pause
    elif request.event_type == "customer.subscription.paused":
        user.toast_active = False
        db.commit()
        logger.info(f"Mock subscription paused for user {user.id}")

    return {
        "status": "success",
        "user_id": user.id,
        "toast_active": user.toast_active,
        "stripe_subscription_id": user.stripe_subscription_id,
        "stripe_customer_id": user.stripe_customer_id,
    }


@test_router.post("/reset-subscription")
async def reset_mock_subscription(
    customer_email: str,
    db: Session = Depends(get_db),
) -> dict:
    """Reset subscription state for a user (cleanup between tests).

    :param customer_email: User email to reset
    :param db: Database session
    :return: dict with status
    """
    user = db.query(User).filter(User.email == customer_email).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {customer_email}")

    user.stripe_customer_id = None
    user.stripe_subscription_id = None
    user.toast_active = False
    db.commit()

    logger.info(f"Reset subscription state for user {user.id}")

    return {
        "status": "success",
        "user_id": user.id,
        "email": user.email,
    }
