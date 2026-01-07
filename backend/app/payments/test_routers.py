"""Mock webhook endpoints for testing Stripe subscription flows."""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.payments.routers import handle_subscription_event
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
    """Trigger webhook events for testing - bypasses signature verification."""

    subscription_data = {
        "id": request.subscription_id,
        "customer": request.customer_id,
        "trial_end": request.trial_end,
    }

    return await handle_subscription_event(
        event_type=request.event_type,
        subscription_data=subscription_data,
        db=db,
    )
