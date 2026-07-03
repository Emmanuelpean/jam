"""Tests for Stripe customer management."""

from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import stripe
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from stripe import StripeObject

from app.payments.customer import create_customer, get_or_create_stripe_customer


def _stripe_customer(**fields) -> StripeObject:
    """Build a StripeObject mimicking a real Stripe Customer response.
    Stripe objects (stripe>=15) use attribute/item access and no longer expose .get()."""

    return StripeObject.construct_from(fields, "sk_test")


class TestCreateCustomer:
    """Tests for _create_customer helper function."""

    @pytest.mark.asyncio
    @patch("app.payments.customer.settings")
    @patch("app.payments.customer.stripe.Customer.create_async", new_callable=AsyncMock)
    async def test_creates_customer_without_test_clock_when_test_mode_false(self, mock_create, mock_settings) -> None:
        """Customer is created without test clock when test_mode is False."""

        mock_settings.test_mode = False
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_customer = MagicMock()
        mock_customer.id = "cus_test123"
        mock_create.return_value = mock_customer

        result = await create_customer(mock_user)

        assert result == mock_customer
        mock_create.assert_called_once_with(
            email="test@example.com",
            metadata={"user_id": "1"},
        )

    @pytest.mark.asyncio
    @patch("app.payments.customer.stripe.test_helpers.TestClock.create_async", new_callable=AsyncMock)
    @patch("app.payments.customer.settings")
    @patch("app.payments.customer.stripe.Customer.create_async", new_callable=AsyncMock)
    async def test_creates_customer_with_test_clock_when_test_mode_true(
        self, mock_create, mock_settings, mock_test_clock_create
    ) -> None:
        """Customer is created with test clock when test_mode is True."""

        mock_settings.test_mode = True
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_test_clock = MagicMock()
        mock_test_clock.id = "clock_test123"
        mock_test_clock_create.return_value = mock_test_clock
        mock_customer = MagicMock()
        mock_customer.id = "cus_test123"
        mock_create.return_value = mock_customer

        result = await create_customer(mock_user)

        assert result == mock_customer
        mock_test_clock_create.assert_called_once()
        # Verify customer was created with test_clock parameter
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["email"] == "test@example.com"
        assert call_kwargs["metadata"] == {"user_id": "1"}
        assert call_kwargs["test_clock"] == "clock_test123"


class TestGetOrCreateStripeCustomer:
    """Tests for get_or_create_stripe_customer function."""

    @pytest.mark.asyncio
    @patch("app.payments.customer.stripe.Customer.retrieve_async", new_callable=AsyncMock)
    async def test_returns_existing_customer_id(self, mock_retrieve) -> None:
        """Returns existing customer_id when user already has one and customer exists."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.stripe_details.customer_id = "cus_existing123"
        mock_db = MagicMock()

        mock_customer = _stripe_customer(id="cus_existing123", email="test@example.com")
        mock_retrieve.return_value = mock_customer

        result = await get_or_create_stripe_customer(mock_user, mock_db)

        assert result == "cus_existing123"
        mock_retrieve.assert_called_once_with("cus_existing123")
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.payments.customer.stripe.Customer.modify_async", new_callable=AsyncMock)
    @patch("app.payments.customer.stripe.Customer.retrieve_async", new_callable=AsyncMock)
    async def test_updates_email_when_mismatch(self, mock_retrieve, mock_modify) -> None:
        """Updates Stripe customer email when it doesn't match user's email."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "new@example.com"
        mock_user.stripe_details.customer_id = "cus_existing123"
        mock_db = MagicMock()

        mock_customer = _stripe_customer(email="old@example.com", id="cus_existing123")
        mock_retrieve.return_value = mock_customer
        mock_modify.return_value = MagicMock(id="cus_existing123")

        result = await get_or_create_stripe_customer(mock_user, mock_db)

        assert result == "cus_existing123"
        mock_modify.assert_called_once_with("cus_existing123", email="new@example.com")

    @pytest.mark.asyncio
    @patch("app.payments.customer.create_customer", new_callable=AsyncMock)
    @patch("app.payments.customer.stripe.Customer.retrieve_async", new_callable=AsyncMock)
    async def test_creates_new_customer_when_existing_is_deleted(self, mock_retrieve, mock_create) -> None:
        """Creates new customer when existing Stripe customer is deleted."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.stripe_details.customer_id = "cus_deleted123"
        mock_db = MagicMock()

        # Simulate deleted customer
        mock_customer = _stripe_customer(deleted=True, id="cus_deleted123")
        mock_retrieve.return_value = mock_customer

        mock_new_customer = MagicMock()
        mock_new_customer.id = "cus_new456"
        mock_create.return_value = mock_new_customer

        result = await get_or_create_stripe_customer(mock_user, mock_db)

        assert result == "cus_new456"
        assert mock_user.stripe_details.customer_id == "cus_new456"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.customer.create_customer", new_callable=AsyncMock)
    async def test_creates_new_customer_when_no_customer_id(self, mock_create) -> None:
        """Creates new customer when user has no customer_id."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.stripe_details.customer_id = None
        mock_db = MagicMock()

        mock_new_customer = MagicMock()
        mock_new_customer.id = "cus_brand_new"
        mock_create.return_value = mock_new_customer

        result = await get_or_create_stripe_customer(mock_user, mock_db)

        assert result == "cus_brand_new"
        assert mock_user.stripe_details.customer_id == "cus_brand_new"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.customer.stripe.Customer.retrieve_async", new_callable=AsyncMock)
    async def test_raises_503_on_stripe_error(self, mock_retrieve) -> None:
        """Raises HTTPException 503 and rolls back on StripeError."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.stripe_details.customer_id = "cus_test"
        mock_db = MagicMock()

        mock_retrieve.side_effect = stripe.error.StripeError("API error")

        with pytest.raises(HTTPException) as exc_info:
            await get_or_create_stripe_customer(mock_user, mock_db)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail and "Payment service temporarily unavailable" in exc_info.value.detail
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.payments.customer.stripe.Customer.retrieve_async", new_callable=AsyncMock)
    async def test_raises_500_on_database_error(self, mock_retrieve) -> None:
        """Raises HTTPException 500 and rolls back on SQLAlchemyError."""

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.stripe_details.customer_id = "cus_test"
        mock_db = MagicMock()

        mock_customer = _stripe_customer(email="test@example.com", id="cus_test", deleted=True)
        mock_retrieve.return_value = mock_customer

        # Simulate database error during commit
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(HTTPException) as exc_info:
            with patch("app.payments.customer.create_customer", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = MagicMock(id="cus_new")
                await get_or_create_stripe_customer(mock_user, mock_db)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail and "An error occurred" in exc_info.value.detail
        mock_db.rollback.assert_called_once()
