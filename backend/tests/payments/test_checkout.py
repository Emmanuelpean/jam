"""Tests for Stripe checkout session building."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.payments.checkout import build_checkout_params


class TestBuildCheckoutParams:
    """Tests for build_checkout_params function."""

    @pytest.mark.asyncio
    async def test_returns_trial_params_for_new_customer(
        self, mock_checkout_settings: MagicMock, mock_subscription_list: AsyncMock
    ) -> None:
        """New customers get 14-day trial with optional payment method."""

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

        mock_subscription_list.assert_called_once_with(customer="cus_new123", status="all", limit=1)

    @pytest.mark.asyncio
    async def test_returns_no_trial_params_for_returning_customer(
        self, mock_checkout_settings: MagicMock, mock_subscription_list: AsyncMock
    ) -> None:
        """Returning customers do not get trial and must provide payment method."""

        # Has previous subscription
        mock_subscription_list.return_value = MagicMock(data=[MagicMock()])

        result = await build_checkout_params("cus_returning123")

        assert result["customer"] == "cus_returning123"
        assert result["mode"] == "subscription"
        assert result["payment_method_collection"] == "always"
        # No trial for returning customers
        assert "trial_period_days" not in result["subscription_data"]
        assert "trial_settings" not in result["subscription_data"]
        assert result["line_items"][0]["price"] == "price_test123"

    @pytest.mark.asyncio
    async def test_includes_correct_urls(
        self, mock_checkout_settings: MagicMock, mock_subscription_list: AsyncMock
    ) -> None:
        """Checkout params include correct success and cancel URLs."""

        mock_checkout_settings.frontend_url = "https://myapp.com"

        result = await build_checkout_params("cus_test")

        assert result["success_url"] == "https://myapp.com/settings/premium?success=true"
        assert result["cancel_url"] == "https://myapp.com/settings/premium?canceled=true"

    @pytest.mark.asyncio
    async def test_uses_hosted_ui_mode(
        self, mock_checkout_settings: MagicMock, mock_subscription_list: AsyncMock
    ) -> None:
        """Checkout params use hosted UI mode with auto locale."""

        result = await build_checkout_params("cus_test")

        assert result["ui_mode"] == "hosted_page"
        assert result["locale"] == "auto"
