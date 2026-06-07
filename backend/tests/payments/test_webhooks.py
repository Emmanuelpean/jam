"""Tests for Stripe webhook processing."""

import datetime as dt
from unittest.mock import patch, MagicMock, AsyncMock

import stripe
from starlette.testclient import TestClient

from app import models

WEBHOOK_URL = "/payments/webhooks"


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


class TestProcessSubscriptionEvent:
    """Tests for webhook endpoint → process_subscription_event."""

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_subscription_created_activates_premium(
        self, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """subscription.created sets subscription_id and activates premium."""

        test_stripe_user.premium.is_active = False
        session.commit()
        mock_retrieve.return_value = MagicMock(status="trialing", trial_end=1735689600)

        response = client.post(
            WEBHOOK_URL,
            json=create_webhook_event(
                "customer.subscription.created", test_stripe_user.stripe_details.customer_id, "sub_new_123"
            ),
        )

        assert response.status_code == 200
        user = session.query(models.User).filter(models.User.id == test_stripe_user.id).first()
        assert user
        assert user.stripe_details.subscription_id == "sub_new_123"
        assert user.premium.is_active is True

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_subscription_deleted_deactivates_premium(
        self, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """subscription.deleted sets premium as inactive."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        test_stripe_user.premium.is_active = True
        session.commit()
        mock_retrieve.return_value = MagicMock(status="canceled", trial_end=None)

        response = client.post(
            WEBHOOK_URL,
            json=create_webhook_event("customer.subscription.deleted", test_stripe_user.stripe_details.customer_id),
        )

        assert response.status_code == 200
        user = session.query(models.User).filter(models.User.id == test_stripe_user.id).first()
        assert user
        assert user.premium.is_active is False

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    @patch("app.payments.webhooks.email_service.send_trial_end_notification")
    def test_trial_will_end_sends_notification(
        self, mock_send_email, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """trial_will_end sends notification email with correct recipient and date."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        email = test_stripe_user.email
        session.commit()
        trial_end_ts = 1735689600.0
        mock_retrieve.return_value = MagicMock(status="trialing", trial_end=trial_end_ts)

        response = client.post(
            WEBHOOK_URL,
            json=create_webhook_event(
                "customer.subscription.trial_will_end",
                test_stripe_user.stripe_details.customer_id,
                trial_end=trial_end_ts,
            ),
        )

        assert response.status_code == 200
        mock_send_email.assert_called_once_with(
            email,
            dt.datetime.fromtimestamp(trial_end_ts),
        )

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    @patch("app.payments.webhooks.email_service.send_trial_end_notification", side_effect=Exception("SMTP error"))
    def test_trial_will_end_email_failure_does_not_crash(
        self, _mock_send_email, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """Email failure during trial_will_end is caught; webhook still returns 200."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_retrieve.return_value = MagicMock(status="trialing", trial_end=1735689600.0)

        response = client.post(
            WEBHOOK_URL,
            json=create_webhook_event(
                "customer.subscription.trial_will_end",
                test_stripe_user.stripe_details.customer_id,
                trial_end=1735689600.0,
            ),
        )

        assert response.status_code == 200

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_ignored_events_succeed_silently(self, mock_retrieve, client: TestClient, test_stripe_user) -> None:
        """Known no-op events (billing_portal.session.created, customer.created) return 200."""

        mock_retrieve.return_value = MagicMock(status=None, trial_end=None)

        for event_type in ["billing_portal.session.created", "customer.created"]:
            response = client.post(
                WEBHOOK_URL, json=create_webhook_event(event_type, test_stripe_user.stripe_details.customer_id)
            )
            assert response.status_code == 200

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_unhandled_event_type_returns_success(self, mock_retrieve, client: TestClient, test_stripe_user) -> None:
        """Unhandled event type logs an error but still returns 200."""

        mock_retrieve.return_value = MagicMock(status=None, trial_end=None)

        response = client.post(
            WEBHOOK_URL,
            json=create_webhook_event("payment_intent.created", test_stripe_user.stripe_details.customer_id),
        )

        assert response.status_code == 200


class TestGetSubscriptionStatus:
    """Tests for get_subscription_status via the webhook flow."""

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_no_subscription_id_skips_stripe_call(
        self, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """User without subscription_id gets None status without calling Stripe."""

        test_stripe_user.stripe_details.subscription_id = None
        session.commit()

        response = client.post(
            WEBHOOK_URL, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 200
        mock_retrieve.assert_not_called()
        user = session.query(models.User).filter(models.User.id == test_stripe_user.id).first()
        assert user
        assert user.stripe_details.subscription_status is None
        assert user.stripe_details.trial_end_date is None

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_retrieves_and_stores_subscription_status(
        self, mock_retrieve, client: TestClient, session, test_stripe_user
    ) -> None:
        """Subscription status and trial_end are fetched from Stripe and persisted."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_retrieve.return_value = MagicMock(status="active", trial_end=1735689600)

        response = client.post(
            WEBHOOK_URL, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 200
        mock_retrieve.assert_called_once_with("sub_existing")
        user = session.query(models.User).filter(models.User.id == test_stripe_user.id).first()
        assert user
        assert user.stripe_details.subscription_status == "active"
        assert user.stripe_details.trial_end_date == 1735689600

    @patch("app.payments.webhooks.stripe.Subscription.retrieve_async", new_callable=AsyncMock)
    def test_stripe_error_returns_400(self, mock_retrieve, client: TestClient, session, test_stripe_user) -> None:
        """StripeError during status retrieval returns HTTP 400."""

        test_stripe_user.stripe_details.subscription_id = "sub_existing"
        session.commit()
        mock_retrieve.side_effect = stripe.error.StripeError("API connection error")

        response = client.post(
            WEBHOOK_URL, json=create_webhook_event("customer.created", test_stripe_user.stripe_details.customer_id)
        )

        assert response.status_code == 400
