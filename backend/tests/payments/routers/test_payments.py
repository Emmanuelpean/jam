"""Tests for the subscription-checkout and customer-portal API endpoints."""

from unittest.mock import AsyncMock

import stripe
from starlette.testclient import TestClient

from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


class TestCreateSubscriptionCheckout(BaseTest):
    """Tests for POST /payments/create-subscription-checkout."""

    endpoint = "/payments/create-subscription-checkout"

    def test_requires_authentication(self, client: TestClient) -> None:
        response = client.post(self.endpoint)
        assert response.status_code == 401

    def test_returns_checkout_url(
        self,
        test_stripe_user: FixtureUser,
        mock_get_or_create_customer: AsyncMock,
        mock_checkout_params: AsyncMock,
        mock_checkout_session: AsyncMock,
    ) -> None:
        mock_checkout_params.return_value = {"mode": "subscription"}

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 200
        assert response.json() == {"url": "https://checkout.stripe.com/c/test"}
        mock_checkout_session.assert_awaited_once_with(mode="subscription")

    def test_internal_http_exception_propagates(
        self,
        test_stripe_user: FixtureUser,
        mock_get_or_create_customer: AsyncMock,
        mock_checkout_params: AsyncMock,
        mock_checkout_session: AsyncMock,
    ) -> None:
        from fastapi import HTTPException, status

        mock_get_or_create_customer.side_effect = HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Customer mismatch"
        )

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 409
        assert response.json()["detail"] == "Customer mismatch"
        # The checkout session is never created once resolving the customer fails
        mock_checkout_params.assert_not_awaited()
        mock_checkout_session.assert_not_awaited()

    def test_stripe_error_returns_400(
        self,
        test_stripe_user: FixtureUser,
        mock_get_or_create_customer: AsyncMock,
        mock_checkout_params: AsyncMock,
        mock_checkout_session: AsyncMock,
    ) -> None:
        mock_checkout_session.side_effect = stripe.error.StripeError("API down")

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 400
        assert "temporarily unavailable" in response.json()["detail"]

    def test_unexpected_error_returns_500(
        self,
        test_stripe_user: FixtureUser,
        mock_get_or_create_customer: AsyncMock,
        mock_checkout_params: AsyncMock,
        mock_checkout_session: AsyncMock,
    ) -> None:
        mock_checkout_session.side_effect = ValueError("boom")

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred. Please try again."


class TestCreatePortalSession(BaseTest):
    """Tests for POST /payments/create-portal-session."""

    endpoint = "/payments/create-portal-session"

    def test_requires_authentication(self, client: TestClient) -> None:
        response = client.post(self.endpoint)
        assert response.status_code == 401

    def test_no_customer_returns_404(self, test_non_premium_user: FixtureUser, mock_portal_session: AsyncMock) -> None:
        response = test_non_premium_user.client.post(self.endpoint)
        assert response.status_code == 404
        assert "No customer found" in response.json()["detail"]
        # No portal session is created when the user has no Stripe customer
        mock_portal_session.assert_not_awaited()

    def test_returns_portal_url(
        self, test_stripe_user: FixtureUser, mock_get_or_create_customer: AsyncMock, mock_portal_session: AsyncMock
    ) -> None:
        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 200
        assert response.json() == {"url": "https://billing.stripe.com/p/test"}

    def test_stripe_error_returns_503(
        self, test_stripe_user: FixtureUser, mock_get_or_create_customer: AsyncMock, mock_portal_session: AsyncMock
    ) -> None:
        mock_portal_session.side_effect = stripe.error.StripeError("API down")

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 503
        assert "temporarily unavailable" in response.json()["detail"]

    def test_unexpected_error_returns_500(
        self, test_stripe_user: FixtureUser, mock_get_or_create_customer: AsyncMock, mock_portal_session: AsyncMock
    ) -> None:
        mock_portal_session.side_effect = ValueError("boom")

        response = test_stripe_user.client.post(self.endpoint)

        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred. Please try again."
