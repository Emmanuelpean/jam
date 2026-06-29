"""Tests for the subscription-checkout and customer-portal API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe
from starlette.testclient import TestClient

from tests.utils import test_data as td

CHECKOUT_URL = "/payments/create-subscription-checkout"
PORTAL_URL = "/payments/create-portal-session"

CUSTOMER_TARGET = "app.payments.routers.payments.get_or_create_stripe_customer"
PARAMS_TARGET = "app.payments.routers.payments.build_checkout_params"
CHECKOUT_TARGET = "app.payments.routers.payments.stripe.checkout.Session.create_async"
PORTAL_TARGET = "app.payments.routers.payments.stripe.billing_portal.Session.create_async"


@pytest.fixture
def stripe_client(authorised_clients) -> TestClient:
    """Authenticated client for the user that has Stripe details (a customer_id)."""
    return authorised_clients[td.STRIPE_USER_INDEX]


@pytest.fixture
def non_premium_client(authorised_clients) -> TestClient:
    """Authenticated client for a user without a Stripe customer_id."""
    return authorised_clients[td.NON_PREMIUM_USER_INDEX]


class TestCreateSubscriptionCheckout:
    """Tests for POST /payments/create-subscription-checkout."""

    def test_requires_authentication(self, client: TestClient) -> None:
        response = client.post(CHECKOUT_URL)
        assert response.status_code == 401

    @patch(CHECKOUT_TARGET, new_callable=AsyncMock)
    @patch(PARAMS_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_returns_checkout_url(
        self, mock_customer, mock_params, mock_session, stripe_client: TestClient
    ) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_params.return_value = {"mode": "subscription"}
        mock_session.return_value = MagicMock(id="cs_test_1", url="https://checkout.stripe.com/c/test")

        response = stripe_client.post(CHECKOUT_URL)

        assert response.status_code == 200
        assert response.json() == {"url": "https://checkout.stripe.com/c/test"}
        mock_session.assert_awaited_once_with(mode="subscription")

    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_internal_http_exception_propagates(self, mock_customer, stripe_client: TestClient) -> None:
        from fastapi import HTTPException, status

        mock_customer.side_effect = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer mismatch")

        response = stripe_client.post(CHECKOUT_URL)

        assert response.status_code == 409
        assert response.json()["detail"] == "Customer mismatch"

    @patch(CHECKOUT_TARGET, new_callable=AsyncMock)
    @patch(PARAMS_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_stripe_error_returns_400(
        self, mock_customer, mock_params, mock_session, stripe_client: TestClient
    ) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_params.return_value = {}
        mock_session.side_effect = stripe.error.StripeError("API down")

        response = stripe_client.post(CHECKOUT_URL)

        assert response.status_code == 400
        assert "temporarily unavailable" in response.json()["detail"]

    @patch(CHECKOUT_TARGET, new_callable=AsyncMock)
    @patch(PARAMS_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_unexpected_error_returns_500(
        self, mock_customer, mock_params, mock_session, stripe_client: TestClient
    ) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_params.return_value = {}
        mock_session.side_effect = ValueError("boom")

        response = stripe_client.post(CHECKOUT_URL)

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred. Please try again."


class TestCreatePortalSession:
    """Tests for POST /payments/create-portal-session."""

    def test_requires_authentication(self, client: TestClient) -> None:
        response = client.post(PORTAL_URL)
        assert response.status_code == 401

    def test_no_customer_returns_404(self, non_premium_client: TestClient) -> None:
        response = non_premium_client.post(PORTAL_URL)
        assert response.status_code == 404
        assert "No customer found" in response.json()["detail"]

    @patch(PORTAL_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_returns_portal_url(self, mock_customer, mock_portal, stripe_client: TestClient) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_portal.return_value = MagicMock(url="https://billing.stripe.com/p/test")

        response = stripe_client.post(PORTAL_URL)

        assert response.status_code == 200
        assert response.json() == {"url": "https://billing.stripe.com/p/test"}

    @patch(PORTAL_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_stripe_error_returns_503(self, mock_customer, mock_portal, stripe_client: TestClient) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_portal.side_effect = stripe.error.StripeError("API down")

        response = stripe_client.post(PORTAL_URL)

        assert response.status_code == 503
        assert "temporarily unavailable" in response.json()["detail"]

    @patch(PORTAL_TARGET, new_callable=AsyncMock)
    @patch(CUSTOMER_TARGET, new_callable=AsyncMock)
    def test_unexpected_error_returns_500(self, mock_customer, mock_portal, stripe_client: TestClient) -> None:
        mock_customer.return_value = "cus_test_123"
        mock_portal.side_effect = ValueError("boom")

        response = stripe_client.post(PORTAL_URL)

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred. Please try again."
