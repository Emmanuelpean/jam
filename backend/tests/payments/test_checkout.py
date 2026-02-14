"""Tests for Stripe checkout session building."""

from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from app.payments.checkout import build_checkout_params


class TestBuildCheckoutParams:
    """Tests for build_checkout_params function."""

    @pytest.mark.asyncio
    @patch("app.payments.checkout.settings")
    @patch("app.payments.checkout.stripe.Subscription.list_async", new_callable=AsyncMock)
    async def test_returns_trial_params_for_new_customer(self, mock_list, mock_settings) -> None:
        """New customers get 14-day trial with optional payment method."""

        mock_settings.stripe_toast_price_id = "price_test123"
        mock_settings.frontend_url = "https://example.com"

        # No previous subscriptions
        mock_list.return_value = MagicMock(data=[])

        result = await build_checkout_params("cus_new123")

        assert result["customer"] == "cus_new123"
        assert result["mode"] == "subscription"
        assert result["payment_method_collection"] == "if_required"
        assert result["subscription_data"]["trial_period_days"] == 14
        assert result["subscription_data"]["trial_settings"]["end_behavior"]["missing_payment_method"] == "cancel"
        assert result["line_items"][0]["price"] == "price_test123"
        assert result["line_items"][0]["quantity"] == 1
        assert result["allow_promotion_codes"] is True
        assert "success=true" in result["success_url"]
        assert "canceled=true" in result["cancel_url"]

        mock_list.assert_called_once_with(customer="cus_new123", status="all", limit=1)

    @pytest.mark.asyncio
    @patch("app.payments.checkout.settings")
    @patch("app.payments.checkout.stripe.Subscription.list_async", new_callable=AsyncMock)
    async def test_returns_no_trial_params_for_returning_customer(self, mock_list, mock_settings) -> None:
        """Returning customers do not get trial and must provide payment method."""

        mock_settings.stripe_toast_price_id = "price_test123"
        mock_settings.frontend_url = "https://example.com"

        # Has previous subscription
        mock_subscription = MagicMock()
        mock_list.return_value = MagicMock(data=[mock_subscription])

        result = await build_checkout_params("cus_returning123")

        assert result["customer"] == "cus_returning123"
        assert result["mode"] == "subscription"
        assert result["payment_method_collection"] == "always"
        # No trial for returning customers
        assert "trial_period_days" not in result["subscription_data"]
        assert "trial_settings" not in result["subscription_data"]
        assert result["line_items"][0]["price"] == "price_test123"

    @pytest.mark.asyncio
    @patch("app.payments.checkout.settings")
    @patch("app.payments.checkout.stripe.Subscription.list_async", new_callable=AsyncMock)
    async def test_includes_correct_urls(self, mock_list, mock_settings) -> None:
        """Checkout params include correct success and cancel URLs."""

        mock_settings.stripe_toast_price_id = "price_test123"
        mock_settings.frontend_url = "https://myapp.com"
        mock_list.return_value = MagicMock(data=[])

        result = await build_checkout_params("cus_test")

        assert result["success_url"] == "https://myapp.com/settings/premium?success=true"
        assert result["cancel_url"] == "https://myapp.com/settings/premium?canceled=true"

    @pytest.mark.asyncio
    @patch("app.payments.checkout.settings")
    @patch("app.payments.checkout.stripe.Subscription.list_async", new_callable=AsyncMock)
    async def test_uses_hosted_ui_mode(self, mock_list, mock_settings) -> None:
        """Checkout params use hosted UI mode with auto locale."""

        mock_settings.stripe_toast_price_id = "price_test123"
        mock_settings.frontend_url = "https://example.com"
        mock_list.return_value = MagicMock(data=[])

        result = await build_checkout_params("cus_test")

        assert result["ui_mode"] == "hosted"
        assert result["locale"] == "auto"
