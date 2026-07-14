"""Tests for Stripe webhook processing."""

import datetime as dt
from unittest.mock import AsyncMock, MagicMock

import pytest
import stripe
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


@pytest.fixture(autouse=True)
def _enable_test_mode(enable_test_mode):
    """The webhook endpoint parses events via stripe.Event.construct_from only under test_mode;
    without it the handler expects a real Stripe signature. Enable it for this module."""

    yield


def create_webhook_event(
    event_type: str,
    customer_id: str,
    subscription_id: str = "sub_test",
    trial_end: float | None = None,
) -> dict:
    """Build a minimal Stripe webhook event payload."""

    obj = {"customer": customer_id, "id": subscription_id}
    if trial_end is not None:
        obj["trial_end"] = trial_end  # noqa
    return {"type": event_type, "data": {"object": obj}}


class TestProcessSubscriptionEvent(BaseTest):
    """Tests for webhook endpoint → process_subscription_event."""

    endpoint = "/payments/webhooks"

    def test_subscription_created_activates_premium(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
    ) -> None:
        """subscription.created sets subscription_id and activates premium."""

        test_stripe_user.premium.is_active = False
        session.commit()
        mock_subscription_retrieve.return_value = MagicMock(status="trialing", trial_end=1735689600)

        response = client.post(
            self.endpoint,
            json=create_webhook_event(
                "customer.subscription.created", test_stripe_user.stripe_details.customer_id, "sub_new_123"
            ),
        )

        assert response.status_code == 200
        user = self.get_user(session, test_stripe_user.id)
        assert user
        assert user.stripe_details.subscription_id == "sub_new_123"
        assert user.premium.is_active is True

    def test_subscription_deleted_deactivates_premium(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
    ) -> None:
        """subscription.deleted sets premium as inactive."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        test_stripe_user.premium.is_active = True
        session.commit()
        mock_subscription_retrieve.return_value = MagicMock(status="canceled", trial_end=None)

        response = client.post(
            self.endpoint,
            json=create_webhook_event("customer.subscription.deleted", test_stripe_user.stripe_details.customer_id),
        )

        assert response.status_code == 200
        user = self.get_user(session, test_stripe_user.id)
        assert user
        assert user.premium.is_active is False

    def test_trial_will_end_sends_notification(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
        mock_trial_end_email: MagicMock,
    ) -> None:
        """trial_will_end sends notification email with correct recipient and date."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        email = test_stripe_user.email
        session.commit()
        trial_end_ts = 1735689600.0
        mock_subscription_retrieve.return_value = MagicMock(status="trialing", trial_end=trial_end_ts)

        response = client.post(
            self.endpoint,
            json=create_webhook_event(
                "customer.subscription.trial_will_end",
                test_stripe_user.stripe_details.customer_id,
                trial_end=trial_end_ts,
            ),
        )

        assert response.status_code == 200
        mock_trial_end_email.assert_called_once_with(
            email,
            dt.datetime.fromtimestamp(trial_end_ts),
        )

    def test_trial_will_end_email_failure_does_not_crash(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
        mock_trial_end_email: MagicMock,
    ) -> None:
        """Email failure during trial_will_end is caught; webhook still returns 200."""

        mock_trial_end_email.side_effect = Exception("SMTP error")
        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_subscription_retrieve.return_value = MagicMock(status="trialing", trial_end=1735689600.0)

        response = client.post(
            self.endpoint,
            json=create_webhook_event(
                "customer.subscription.trial_will_end",
                test_stripe_user.stripe_details.customer_id,
                trial_end=1735689600.0,
            ),
        )

        assert response.status_code == 200

    def test_ignored_events_succeed_silently(
        self, client: TestClient, test_stripe_user: FixtureUser, mock_subscription_retrieve: AsyncMock
    ) -> None:
        """Known no-op events (billing_portal.session.created, customer.created) return 200."""

        for event_type in ["billing_portal.session.created", "customer.created"]:
            response = client.post(
                self.endpoint, json=create_webhook_event(event_type, test_stripe_user.stripe_details.customer_id)
            )
            assert response.status_code == 200

    def test_unhandled_event_type_returns_success(
        self, client: TestClient, test_stripe_user: FixtureUser, mock_subscription_retrieve: AsyncMock
    ) -> None:
        """Unhandled event type logs an error but still returns 200."""

        response = client.post(
            self.endpoint,
            json=create_webhook_event("payment_intent.created", test_stripe_user.stripe_details.customer_id),
        )

        assert response.status_code == 200


class TestWebhookEndpointGuards(BaseTest):
    """Tests for the webhook endpoint's request-validation branches."""

    endpoint = "/payments/webhooks"

    def test_missing_customer_returns_400(self, client: TestClient) -> None:
        """An event whose object has no customer id is rejected with 400."""

        payload = {"type": "customer.subscription.created", "data": {"object": {"id": "sub_x"}}}
        response = client.post(self.endpoint, json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid customer ID"

    def test_invalid_payload_returns_400(self, client: TestClient, mock_webhook_construct: MagicMock) -> None:
        """A payload that cannot be parsed in production mode returns 400."""

        mock_webhook_construct.side_effect = ValueError("bad payload")

        response = client.post(self.endpoint, content=b"{}", headers={"stripe-signature": "sig"})

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid payload"

    def test_invalid_signature_returns_400(self, client: TestClient, mock_webhook_construct: MagicMock) -> None:
        """A signature that fails verification in production mode returns 400."""

        mock_webhook_construct.side_effect = stripe.error.SignatureVerificationError("bad sig", "sig")

        response = client.post(self.endpoint, content=b"{}", headers={"stripe-signature": "sig"})

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"


class TestGetSubscriptionStatus(BaseTest):
    """Tests for get_subscription_status via the webhook flow."""

    endpoint = "/payments/webhooks"

    def test_no_subscription_id_skips_stripe_call(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
    ) -> None:
        """User without subscription_id gets None status without calling Stripe."""

        test_stripe_user.stripe_details.subscription_id = None
        session.commit()

        response = client.post(
            self.endpoint, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 200
        mock_subscription_retrieve.assert_not_called()
        user = self.get_user(session, test_stripe_user.id)
        assert user
        assert user.stripe_details.subscription_status is None
        assert user.stripe_details.trial_end_date is None

    def test_retrieves_and_stores_subscription_status(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
    ) -> None:
        """Subscription status and trial_end are fetched from Stripe and persisted."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_subscription_retrieve.return_value = MagicMock(status="active", trial_end=1735689600)

        response = client.post(
            self.endpoint, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 200
        mock_subscription_retrieve.assert_called_once_with("sub_existing")
        user = self.get_user(session, test_stripe_user.id)
        assert user
        assert user.stripe_details.subscription_status == "active"
        assert user.stripe_details.trial_end_date == 1735689600

    def test_stripe_error_returns_400(
        self,
        client: TestClient,
        session: Session,
        test_stripe_user: FixtureUser,
        mock_subscription_retrieve: AsyncMock,
    ) -> None:
        """StripeError during status retrieval returns HTTP 400."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_subscription_retrieve.side_effect = stripe.error.StripeError("API connection error")

        response = client.post(
            self.endpoint, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 400
