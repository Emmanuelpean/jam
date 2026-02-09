"""Tests for Stripe product setup script."""

from unittest.mock import patch, MagicMock

from app.payments.setup import setup_stripe_products


class TestSetupStripeProducts:
    """Tests for setup_stripe_products."""

    @patch("app.payments.setup.stripe.Price.create")
    @patch("app.payments.setup.stripe.Product.create")
    def test_creates_product_and_price_with_correct_params(self, mock_product_create, mock_price_create) -> None:
        """Product and price are created with the expected parameters."""

        mock_product_create.return_value = MagicMock(id="prod_test_123")
        mock_price_create.return_value = MagicMock(id="price_test_456")

        setup_stripe_products()

        mock_product_create.assert_called_once_with(name="TOAST")
        mock_price_create.assert_called_once_with(
            product="prod_test_123",
            unit_amount=500,
            currency="GBP",
            recurring={"interval": "month"},
        )

    @patch("app.payments.setup.stripe.Price.create")
    @patch("app.payments.setup.stripe.Product.create")
    def test_prints_created_ids(self, mock_product_create, mock_price_create, capsys) -> None:
        """Created product and price IDs are printed to stdout."""

        mock_product_create.return_value = MagicMock(id="prod_abc")
        mock_price_create.return_value = MagicMock(id="price_xyz")

        setup_stripe_products()

        output = capsys.readouterr().out
        assert "prod_abc" in output
        assert "price_xyz" in output

    @patch("app.payments.setup.stripe.Price.create")
    @patch("app.payments.setup.stripe.Product.create")
    def test_price_uses_product_id_from_created_product(self, mock_product_create, mock_price_create) -> None:
        """Price creation receives the id returned by Product.create, not a hardcoded value."""

        mock_product_create.return_value = MagicMock(id="prod_dynamic_id")
        mock_price_create.return_value = MagicMock(id="price_irrelevant")

        setup_stripe_products()

        mock_price_create.assert_called_once()
        assert mock_price_create.call_args[1]["product"] == "prod_dynamic_id"
