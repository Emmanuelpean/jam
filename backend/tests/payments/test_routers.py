"""Unit tests for Stripe payment integration."""

import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.payments.webhooks import (
    create_subscription_checkout,
    create_portal_session,
    get_subscription_status,
    stripe_webhook,
    handle_subscription_event,
    SubscriptionRequest,
)


class TestCreateSubscriptionCheckout:
    """Test class for subscription checkout creation."""

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.list_async")
    @patch("app.payments.routers.stripe.checkout.Session.create_async")
    async def test_create_checkout_existing_customer(self, mock_checkout_create, mock_customer_list) -> None:
        """Test checkout creation with existing customer."""
        mock_customer = Mock(id="cus_123", email="test@example.com")
        mock_customer_list.return_value = Mock(data=[mock_customer])
        mock_checkout_create.return_value = Mock(client_secret="cs_test_secret")

        request = SubscriptionRequest(customer_email="test@example.com")
        result = await create_subscription_checkout(request)

        assert result == {"clientSecret": "cs_test_secret"}
        mock_customer_list.assert_called_once_with(email="test@example.com", limit=1)
        mock_checkout_create.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.list_async")
    @patch("app.payments.routers.stripe.Customer.create_async")
    @patch("app.payments.routers.stripe.checkout.Session.create_async")
    async def test_create_checkout_new_customer(
        self, mock_checkout_create, mock_customer_create, mock_customer_list
    ) -> None:
        """Test checkout creation with new customer."""
        mock_customer_list.return_value = Mock(data=[])
        mock_customer_create.return_value = Mock(id="cus_456", email="new@example.com")
        mock_checkout_create.return_value = Mock(client_secret="cs_test_secret")

        request = SubscriptionRequest(customer_email="new@example.com")
        result = await create_subscription_checkout(request)

        assert result == {"clientSecret": "cs_test_secret"}
        mock_customer_create.assert_called_once_with(email="new@example.com")

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.list_async")
    async def test_create_checkout_stripe_error(self, mock_customer_list) -> None:
        """Test checkout creation with Stripe API error."""
        mock_customer_list.side_effect = Exception("Stripe API error")

        request = SubscriptionRequest(customer_email="test@example.com")

        with pytest.raises(HTTPException) as exc_info:
            await create_subscription_checkout(request)

        assert exc_info.value.status_code == 400
        assert "Stripe API error" in str(exc_info.value.detail)


class TestCreatePortalSession:
    """Test class for customer portal session creation."""

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.list_async")
    @patch("app.payments.routers.stripe.billing_portal.Session.create_async")
    async def test_create_portal_session_success(self, mock_portal_create, mock_customer_list) -> None:
        """Test successful portal session creation."""
        mock_customer = Mock(id="cus_123", email="test@example.com")
        mock_customer_list.return_value = Mock(data=[mock_customer])
        mock_portal_create.return_value = Mock(url="https://billing.stripe.com/session")

        request = SubscriptionRequest(customer_email="test@example.com")
        result = await create_portal_session(request)

        assert result == {"url": "https://billing.stripe.com/session"}
        mock_portal_create.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.list_async")
    async def test_create_portal_session_customer_not_found(self, mock_customer_list) -> None:
        """Test portal session creation when customer doesn't exist."""

        mock_customer_list.return_value = Mock(data=[])

        request = SubscriptionRequest(customer_email="nonexistent@example.com")

        with pytest.raises(HTTPException) as exc_info:
            await create_portal_session(request)

        assert exc_info.value.status_code == 404
        assert "Customer not found" in exc_info.value.detail


class TestGetSubscriptionStatus:
    """Test class for subscription status retrieval."""

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Subscription.retrieve_async")
    async def test_get_status_active_subscription(self, mock_retrieve) -> None:
        """Test retrieving active subscription status."""
        mock_retrieve.return_value = Mock(status="active", trial_end=None)

        result = await get_subscription_status("sub_123")

        assert result["status"] == "active"
        assert result["trial_end"] is None
        assert result["trial_days_remaining"] is None

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Subscription.retrieve_async")
    @patch("time.time")
    async def test_get_status_trialing_subscription(self, mock_time, mock_retrieve) -> None:
        """Test retrieving trialing subscription with remaining days."""
        current_time = 1000000
        mock_time.return_value = current_time
        trial_end = current_time + 86400 * 7  # 7 days remaining

        mock_retrieve.return_value = Mock(status="trialing", trial_end=trial_end)

        result = await get_subscription_status("sub_123")

        assert result["status"] == "trialing"
        assert result["trial_end"] == trial_end
        assert result["trial_days_remaining"] == 7

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Subscription.retrieve_async")
    @patch("time.time")
    async def test_get_status_trial_expired(self, mock_time, mock_retrieve) -> None:
        """Test retrieving subscription with expired trial."""
        current_time = 1000000
        mock_time.return_value = current_time
        trial_end = current_time - 86400  # Trial ended yesterday

        mock_retrieve.return_value = Mock(status="trialing", trial_end=trial_end)

        result = await get_subscription_status("sub_123")

        assert result["trial_days_remaining"] == 0  # Never negative

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Subscription.retrieve_async")
    async def test_get_status_stripe_error(self, mock_retrieve) -> None:
        """Test subscription status retrieval with Stripe error."""

        mock_retrieve.side_effect = stripe.error.StripeError("Invalid subscription ID")

        with pytest.raises(HTTPException) as exc_info:
            await get_subscription_status("invalid_sub")

        assert exc_info.value.status_code == 400


class TestHandleSubscriptionEvent:
    """Test class for webhook event handling."""

    @pytest.fixture
    def mock_db(self) -> Mock:
        """Create mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user(self) -> Mock:
        """Create mock user with default values."""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        user.stripe_customer_id = "cus_123"
        user.stripe_subscription_id = None
        user.toast_active = False
        return user

    @pytest.mark.asyncio
    async def test_subscription_created_event(self, mock_db, mock_user) -> None:
        """Test handling subscription created event."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        subscription_data = {"id": "sub_123", "customer": "cus_123"}

        result = await handle_subscription_event("customer.subscription.created", subscription_data, mock_db)

        assert result["status"] == "success"
        assert mock_user.stripe_subscription_id == "sub_123"
        assert mock_user.toast_active is True
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_deleted_event(self, mock_db, mock_user) -> None:
        """Test handling subscription deleted event."""
        mock_user.stripe_subscription_id = "sub_123"
        mock_user.toast_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        subscription_data = {"id": "sub_123", "customer": "cus_123"}

        result = await handle_subscription_event("customer.subscription.deleted", subscription_data, mock_db)

        assert result["status"] == "success"
        assert mock_user.stripe_subscription_id is None
        assert mock_user.toast_active is False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.routers.email_service.send_trial_end_notification")
    async def test_trial_will_end_event(self, mock_email, mock_db, mock_user) -> None:
        """Test handling trial ending soon event."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        trial_end_timestamp = int(time.time()) + 86400 * 3  # 3 days from now
        subscription_data = {"id": "sub_123", "customer": "cus_123", "trial_end": trial_end_timestamp}

        result = await handle_subscription_event("customer.subscription.trial_will_end", subscription_data, mock_db)

        assert result["status"] == "success"
        mock_email.assert_called_once()
        # Verify email was called with user email and trial end date
        call_args = mock_email.call_args[0]
        assert call_args[0] == mock_user.email

    @pytest.mark.asyncio
    @patch("app.payments.routers.email_service.send_trial_end_notification")
    async def test_trial_will_end_email_failure(self, mock_email, mock_db, mock_user) -> None:
        """Test trial ending event when email sending fails."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_email.side_effect = Exception("Email service error")

        subscription_data = {"id": "sub_123", "customer": "cus_123", "trial_end": int(time.time()) + 86400 * 3}

        # Should not raise exception, just log error
        result = await handle_subscription_event("customer.subscription.trial_will_end", subscription_data, mock_db)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_subscription_paused_event(self, mock_db, mock_user) -> None:
        """Test handling subscription paused event."""
        mock_user.toast_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        subscription_data = {"id": "sub_123", "customer": "cus_123"}

        result = await handle_subscription_event("customer.subscription.paused", subscription_data, mock_db)

        assert result["status"] == "success"
        assert mock_user.toast_active is False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_unhandled_event_type(self, mock_db, mock_user) -> None:
        """Test handling unknown event type."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        subscription_data = {"id": "sub_123", "customer": "cus_123"}

        result = await handle_subscription_event("customer.subscription.unknown_event", subscription_data, mock_db)

        assert result["status"] == "success"
        # Should not crash or modify user

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.retrieve_async")
    async def test_event_links_new_customer(self, mock_customer_retrieve, mock_db, mock_user) -> None:
        """Test event handler links customer to user when not linked."""
        mock_customer = Mock(email="test@example.com")
        mock_customer_retrieve.return_value = mock_customer

        # First query returns None (no user with customer_id)
        # Second query returns user (found by email)
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_user]

        subscription_data = {"id": "sub_123", "customer": "cus_new"}

        result = await handle_subscription_event("customer.subscription.created", subscription_data, mock_db)

        assert result["status"] == "success"
        assert mock_user.stripe_customer_id == "cus_new"
        assert mock_user.stripe_subscription_id == "sub_123"
        assert mock_db.commit.call_count == 2  # Once for linking, once for subscription

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Customer.retrieve_async")
    async def test_event_customer_not_found_by_email(self, mock_customer_retrieve, mock_db) -> None:
        """Test event when customer exists but user doesn't."""
        mock_customer = Mock(email="nonexistent@example.com")
        mock_customer_retrieve.return_value = mock_customer

        # No user found by customer_id or email
        mock_db.query.return_value.filter.return_value.first.return_value = None

        subscription_data = {"id": "sub_123", "customer": "cus_orphan"}

        result = await handle_subscription_event("customer.subscription.created", subscription_data, mock_db)

        assert result["status"] == "user_not_found"


class TestStripeWebhook:
    """Test class for Stripe webhook endpoint."""

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Webhook.construct_event")
    @patch("app.payments.routers.handle_subscription_event")
    async def test_webhook_valid_signature(self, mock_handle_event, mock_construct_event) -> None:
        """Test webhook with valid signature."""
        mock_request = Mock()
        mock_request.body = AsyncMock(return_value=b'{"type": "customer.subscription.created"}')
        mock_request.headers.get.return_value = "valid_signature"

        mock_event = Mock()
        mock_event.type = "customer.subscription.created"
        mock_event.data.object = {"id": "sub_123", "customer": "cus_123"}
        mock_construct_event.return_value = mock_event

        mock_handle_event.return_value = {"status": "success"}
        mock_db = Mock()

        result = await stripe_webhook(mock_request, mock_db)

        assert result["status"] == "success"
        mock_handle_event.assert_called_once_with(
            event_type="customer.subscription.created",
            subscription_data={"id": "sub_123", "customer": "cus_123"},
            db=mock_db,
        )

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Webhook.construct_event")
    async def test_webhook_invalid_signature(self, mock_construct_event) -> None:
        """Test webhook with invalid signature."""

        mock_request = Mock()
        mock_request.body = AsyncMock(return_value=b"{}")
        mock_request.headers.get.return_value = "invalid_signature"
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "sig_header")

        mock_db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await stripe_webhook(mock_request, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid signature" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Webhook.construct_event")
    async def test_webhook_invalid_payload(self, mock_construct_event) -> None:
        """Test webhook with invalid JSON payload."""
        mock_request = Mock()
        mock_request.body = AsyncMock(return_value=b"invalid json")
        mock_request.headers.get.return_value = "valid_signature"
        mock_construct_event.side_effect = ValueError("Invalid payload")

        mock_db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await stripe_webhook(mock_request, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid payload" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.payments.routers.stripe.Webhook.construct_event")
    @patch("app.payments.routers.handle_subscription_event")
    async def test_webhook_multiple_event_types(self, mock_handle_event, mock_construct_event, mock_db=Mock()) -> None:
        """Test webhook handles different event types correctly."""
        event_types = ["customer.subscription.created", "customer.subscription.deleted", "customer.subscription.paused"]

        for event_type in event_types:
            mock_request = Mock()
            mock_request.body = AsyncMock(return_value=b"{}")
            mock_request.headers.get.return_value = "valid_sig"

            mock_event = Mock()
            mock_event.type = event_type
            mock_event.data.object = {"id": "sub_123", "customer": "cus_123"}
            mock_construct_event.return_value = mock_event

            mock_handle_event.return_value = {"status": "success"}

            result = await stripe_webhook(mock_request, mock_db)

            assert result["status"] == "success"
