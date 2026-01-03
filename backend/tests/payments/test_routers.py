"""Tests for Stripe payment endpoints."""

from unittest.mock import MagicMock, patch

import pytest
import stripe
from fastapi import status

from app.model_registry import User


@pytest.fixture
def mock_stripe_customer() -> MagicMock:
    """Mock Stripe customer object"""

    customer = MagicMock()
    customer.id = "cus_test123"
    customer.email = "test@example.com"
    return customer


@pytest.fixture
def mock_stripe_session() -> MagicMock:
    """Mock Stripe checkout session object"""

    session = MagicMock()
    session.id = "cs_test_123"
    session.client_secret = "cs_test_a1b2c3d4e5f6g7h8"
    session.url = "https://checkout.stripe.com/test"
    return session


class TestCreateSubscriptionCheckout:
    """Tests for /payments/create-subscription-checkout endpoint"""

    @pytest.mark.asyncio
    @patch("stripe.Customer.list_async")
    @patch("stripe.Customer.create_async")
    @patch("stripe.checkout.Session.create_async")
    async def test_create_subscription_new_customer(
        self,
        mock_session_create,
        mock_customer_create,
        mock_customer_list,
        client,
        mock_stripe_customer,
        mock_stripe_session,
    ) -> None:
        """Test creating checkout session for new customer"""

        # Setup mocks
        mock_list_result = MagicMock()
        mock_list_result.data = []  # No existing customer
        mock_customer_list.return_value = mock_list_result
        mock_customer_create.return_value = mock_stripe_customer
        mock_session_create.return_value = mock_stripe_session

        # Make request
        response = client.post("/payments/create-subscription-checkout", json={"customer_email": "newuser@example.com"})

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "clientSecret" in data
        assert data["clientSecret"] == "cs_test_a1b2c3d4e5f6g7h8"

        # Verify Stripe API was called correctly
        mock_customer_list.assert_called_once()
        mock_customer_create.assert_called_once_with(email="newuser@example.com")
        mock_session_create.assert_called_once()

    @pytest.mark.asyncio
    @patch("stripe.Customer.list_async")
    @patch("stripe.checkout.Session.create_async")
    async def test_create_subscription_existing_customer(
        self, mock_session_create, mock_customer_list, client, mock_stripe_customer, mock_stripe_session
    ) -> None:
        """Test creating checkout session for existing customer"""
        # Setup mocks - customer already exists
        mock_list_result = MagicMock()
        mock_list_result.data = [mock_stripe_customer]
        mock_customer_list.return_value = mock_list_result
        mock_session_create.return_value = mock_stripe_session

        # Make request
        response = client.post(
            "/payments/create-subscription-checkout", json={"customer_email": "existing@example.com"}
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "clientSecret" in data

    @pytest.mark.asyncio
    @patch("stripe.Customer.list_async")
    async def test_create_subscription_stripe_error(self, mock_customer_list, client) -> None:
        """Test handling Stripe API errors"""

        # Simulate Stripe error
        mock_customer_list.side_effect = Exception("Stripe API error")

        # Make request
        response = client.post("/payments/create-subscription-checkout", json={"customer_email": "test@example.com"})

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Stripe API error" in response.json()["detail"]

    def test_create_subscription_missing_email(self, client) -> None:
        """Test with missing email field"""

        response = client.post("/payments/create-subscription-checkout", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStripeWebhook:
    """Tests for /payments/webhook endpoint"""

    @pytest.fixture
    def subscription_created_event(self) -> dict:
        """Mock webhook payload for subscription.created"""

        return {
            "type": "customer.subscription.created",
            "data": {"object": {"id": "sub_test123", "customer": "cus_test123"}},
        }

    @pytest.fixture
    def subscription_deleted_event(self) -> dict:
        """Mock webhook payload for subscription.deleted"""

        return {
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_test123", "customer": "cus_test123"}},
        }

    @pytest.mark.asyncio
    @patch("stripe.Webhook.construct_event")
    @patch("stripe.Customer.retrieve_async")
    async def test_webhook_subscription_created(
        self,
        mock_customer_retrieve,
        mock_construct_event,
        client,
        session,
        test_regular_user,
        subscription_created_event,
    ) -> None:
        """Test webhook handling for subscription created"""

        # Setup mocks
        mock_construct_event.return_value = subscription_created_event

        mock_customer = MagicMock()
        mock_customer.email = test_regular_user.email
        mock_customer_retrieve.return_value = mock_customer
        user_id = test_regular_user.id

        # Make webhook request
        response = client.post(
            "/payments/webhook", json=subscription_created_event, headers={"stripe-signature": "test_signature"}
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

        # Verify database was updated
        user = session.query(User).filter(User.id == user_id).first()
        assert user.toast_active is True

    @pytest.mark.asyncio
    @patch("stripe.Webhook.construct_event")
    @patch("stripe.Customer.retrieve_async")
    async def test_webhook_subscription_deleted(
        self,
        mock_customer_retrieve,
        mock_construct_event,
        client,
        session,
        test_regular_user,
        subscription_deleted_event,
    ) -> None:
        """Test webhook handling for subscription deleted"""

        # Set user as active first
        test_regular_user.toast_active = True
        session.commit()

        # Setup mocks
        mock_construct_event.return_value = subscription_deleted_event

        mock_customer = MagicMock()
        mock_customer.email = test_regular_user.email
        mock_customer_retrieve.return_value = mock_customer
        user_id = test_regular_user.id

        # Make webhook request
        response = client.post(
            "/payments/webhook", json=subscription_deleted_event, headers={"stripe-signature": "test_signature"}
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK

        # Verify database was updated
        user = session.query(User).filter(User.id == user_id).first()
        assert user.toast_active is False

    @pytest.mark.asyncio
    @patch("stripe.Webhook.construct_event")
    async def test_webhook_invalid_signature(self, mock_construct_event, client) -> None:
        """Test webhook with invalid signature"""

        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "sig")
        response = client.post("/payments/webhook", json={}, headers={"stripe-signature": "invalid_signature"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid signature" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch("stripe.Webhook.construct_event")
    async def test_webhook_invalid_payload(self, mock_construct_event, client) -> None:
        """Test webhook with invalid payload"""

        mock_construct_event.side_effect = ValueError("Invalid payload")
        response = client.post("/payments/webhook", json={}, headers={"stripe-signature": "test_signature"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid payload" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch("stripe.Webhook.construct_event")
    @patch("stripe.Customer.retrieve_async")
    async def test_webhook_user_not_found(
        self, mock_customer_retrieve, mock_construct_event, client, subscription_created_event
    ) -> None:
        """Test webhook when user doesn't exist in database"""

        # Setup mocks
        mock_construct_event.return_value = subscription_created_event

        mock_customer = MagicMock()
        mock_customer.email = "nonexistent@example.com"  # User doesn't exist
        mock_customer_retrieve.return_value = mock_customer

        # Make webhook request
        response = client.post(
            "/payments/webhook", json=subscription_created_event, headers={"stripe-signature": "test_signature"}
        )

        # Should still return success (webhook received)
        # but no database update happens
        assert response.status_code == status.HTTP_200_OK
