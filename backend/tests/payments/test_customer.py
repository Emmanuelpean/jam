"""Tests for Stripe customer management."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import stripe
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from stripe import StripeObject

from app.payments.customer import create_customer, get_or_create_stripe_customer
from tests.fixtures.users import FixtureUser


def _stripe_customer(**fields) -> StripeObject:
    """Build a StripeObject mimicking a real Stripe Customer response.
    Stripe objects (stripe>=15) use attribute/item access and no longer expose .get()."""

    return StripeObject.construct_from(fields, "sk_test")


class TestCreateCustomer:
    """Tests for create_customer helper function."""

    @pytest.mark.asyncio
    async def test_creates_customer_without_test_clock_when_test_mode_false(
        self, mock_customer_settings: MagicMock, mock_customer_create: AsyncMock, test_stripe_user: FixtureUser
    ) -> None:
        """Customer is created without test clock when test_mode is False."""

        customer = MagicMock(id="cus_test123")
        mock_customer_create.return_value = customer

        result = await create_customer(test_stripe_user)

        assert result == customer
        mock_customer_create.assert_called_once_with(
            email=test_stripe_user.email,
            metadata={"user_id": str(test_stripe_user.id)},
        )

    @pytest.mark.asyncio
    async def test_creates_customer_with_test_clock_when_test_mode_true(
        self,
        mock_customer_settings: MagicMock,
        mock_customer_create: AsyncMock,
        mock_test_clock_create: AsyncMock,
        test_stripe_user: FixtureUser,
    ) -> None:
        """Customer is created with test clock when test_mode is True."""

        mock_customer_settings.test_mode = True
        mock_test_clock_create.return_value = MagicMock(id="clock_test123")
        customer = MagicMock(id="cus_test123")
        mock_customer_create.return_value = customer

        result = await create_customer(test_stripe_user)

        assert result == customer
        mock_test_clock_create.assert_called_once()
        # Verify customer was created with test_clock parameter
        call_kwargs = mock_customer_create.call_args[1]
        assert call_kwargs["email"] == test_stripe_user.email
        assert call_kwargs["metadata"] == {"user_id": str(test_stripe_user.id)}
        assert call_kwargs["test_clock"] == "clock_test123"


class TestGetOrCreateStripeCustomer:
    """Tests for get_or_create_stripe_customer function."""

    @pytest.mark.asyncio
    async def test_returns_existing_customer_id(
        self, mock_customer_retrieve: AsyncMock, test_stripe_user: FixtureUser, mock_db: MagicMock
    ) -> None:
        """Returns existing customer_id when user already has one and customer exists."""

        customer_id = test_stripe_user.stripe_details.customer_id
        mock_customer_retrieve.return_value = _stripe_customer(id=customer_id, email=test_stripe_user.email)

        result = await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert result == customer_id
        mock_customer_retrieve.assert_called_once_with(customer_id)
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_email_when_mismatch(
        self,
        mock_customer_retrieve: AsyncMock,
        mock_customer_modify: AsyncMock,
        test_stripe_user: FixtureUser,
        mock_db: MagicMock,
    ) -> None:
        """Updates Stripe customer email when it doesn't match user's email."""

        test_stripe_user.email = "new@example.com"
        customer_id = test_stripe_user.stripe_details.customer_id
        mock_customer_retrieve.return_value = _stripe_customer(email="old@example.com", id=customer_id)
        mock_customer_modify.return_value = MagicMock(id=customer_id)

        result = await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert result == customer_id
        mock_customer_modify.assert_called_once_with(customer_id, email="new@example.com")

    @pytest.mark.asyncio
    async def test_creates_new_customer_when_existing_is_deleted(
        self,
        mock_customer_retrieve: AsyncMock,
        mock_create_customer: AsyncMock,
        test_stripe_user: FixtureUser,
        mock_db: MagicMock,
    ) -> None:
        """Creates new customer when existing Stripe customer is deleted."""

        # Simulate deleted customer
        mock_customer_retrieve.return_value = _stripe_customer(
            deleted=True, id=test_stripe_user.stripe_details.customer_id
        )
        mock_create_customer.return_value = MagicMock(id="cus_new456")

        result = await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert result == "cus_new456"
        assert test_stripe_user.stripe_details.customer_id == "cus_new456"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_new_customer_when_no_customer_id(
        self, mock_create_customer: AsyncMock, test_stripe_user: FixtureUser, mock_db: MagicMock
    ) -> None:
        """Creates new customer when user has no customer_id."""

        test_stripe_user.stripe_details.customer_id = None
        mock_create_customer.return_value = MagicMock(id="cus_brand_new")

        result = await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert result == "cus_brand_new"
        assert test_stripe_user.stripe_details.customer_id == "cus_brand_new"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_503_on_stripe_error(
        self, mock_customer_retrieve: AsyncMock, test_stripe_user: FixtureUser, mock_db: MagicMock
    ) -> None:
        """Raises HTTPException 503 and rolls back on StripeError."""

        mock_customer_retrieve.side_effect = stripe.error.StripeError("API error")

        with pytest.raises(HTTPException) as exc_info:
            await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail and "Payment service temporarily unavailable" in exc_info.value.detail
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_500_on_database_error(
        self,
        mock_customer_retrieve: AsyncMock,
        mock_create_customer: AsyncMock,
        test_stripe_user: FixtureUser,
        mock_db: MagicMock,
    ) -> None:
        """Raises HTTPException 500 and rolls back on SQLAlchemyError."""

        mock_customer_retrieve.return_value = _stripe_customer(
            email=test_stripe_user.email, id=test_stripe_user.stripe_details.customer_id, deleted=True
        )
        mock_create_customer.return_value = MagicMock(id="cus_new")
        # Simulate database error during commit
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_or_create_stripe_customer(test_stripe_user, mock_db)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail and "An error occurred" in exc_info.value.detail
        mock_db.rollback.assert_called_once()
