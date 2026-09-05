"""Shared mock fixtures for the payments test suite.

Two groups:

- Stripe SDK mocks patch the SDK at its canonical path (e.g. ``stripe.Customer.create_async``). Every
  payments module imports the same ``stripe`` object (re-exported from ``app.payments``), so patching
  here takes effect across all of them.
- Module-bound mocks patch a name inside a specific payments module (its ``settings``, an internal
  helper, or a router dependency), so their targets are module paths rather than canonical ``stripe.*``.

The autouse ``block_real_stripe_requests`` guard in the top-level conftest blocks any un-mocked Stripe
call from reaching the network, so a test only needs these when it actually drives that call.
"""

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ----------------------------------------------------- Stripe SDK -----------------------------------------------------


@pytest.fixture
def mock_customer_create() -> Iterator[AsyncMock]:
    """Patch Stripe customer creation."""
    with patch("stripe.Customer.create_async", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_customer_retrieve() -> Iterator[AsyncMock]:
    """Patch Stripe customer retrieval."""
    with patch("stripe.Customer.retrieve_async", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_customer_modify() -> Iterator[AsyncMock]:
    """Patch Stripe customer modification."""
    with patch("stripe.Customer.modify_async", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_test_clock_create() -> Iterator[AsyncMock]:
    """Patch Stripe test-clock creation."""
    with patch("stripe.test_helpers.TestClock.create_async", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_subscription_list() -> Iterator[AsyncMock]:
    """Patch Stripe subscription listing, defaulting to a customer with no prior subscriptions."""
    with patch("stripe.Subscription.list_async", new_callable=AsyncMock) as mock:
        mock.return_value = MagicMock(data=[])
        yield mock


@pytest.fixture
def mock_checkout_session() -> Iterator[AsyncMock]:
    """Patch Stripe checkout-session creation, defaulting to a session with a checkout url."""
    with patch("stripe.checkout.Session.create_async", new_callable=AsyncMock) as mock:
        mock.return_value = MagicMock(id="cs_test_1", url="https://checkout.stripe.com/c/test")
        yield mock


@pytest.fixture
def mock_portal_session() -> Iterator[AsyncMock]:
    """Patch Stripe billing-portal creation, defaulting to a session with a portal url."""
    with patch("stripe.billing_portal.Session.create_async", new_callable=AsyncMock) as mock:
        mock.return_value = MagicMock(url="https://billing.stripe.com/p/test")
        yield mock


@pytest.fixture
def mock_subscription_retrieve() -> Iterator[AsyncMock]:
    """Patch Stripe subscription retrieval, defaulting to a subscription with no status or trial."""
    with patch("stripe.Subscription.retrieve_async", new_callable=AsyncMock) as mock:
        mock.return_value = MagicMock(status=None, trial_end=None)
        yield mock


# ---------------------------------------------------- Module-bound ----------------------------------------------------


@pytest.fixture
def mock_db() -> MagicMock:
    """A stand-in database session for asserting commit/rollback calls."""
    return MagicMock()


@pytest.fixture
def mock_customer_settings() -> Iterator[MagicMock]:
    """Patch the customer module's settings, defaulting to test_mode off."""
    with patch("app.payments.customer.settings") as mock:
        mock.test_mode = False
        yield mock


@pytest.fixture
def mock_checkout_settings() -> Iterator[MagicMock]:
    """Patch the checkout module's settings with test price id and frontend url."""
    with patch("app.payments.checkout.settings") as mock:
        mock.stripe_premium_price_id = "price_test123"
        mock.frontend_url = "https://example.com"
        yield mock


@pytest.fixture
def mock_create_customer() -> Iterator[AsyncMock]:
    """Patch the customer module's create_customer helper."""
    with patch("app.payments.customer.create_customer", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_get_or_create_customer() -> Iterator[AsyncMock]:
    """Patch the payments router's Stripe-customer resolver, defaulting to an existing customer id."""
    with patch("app.payments.routers.payments.get_or_create_stripe_customer", new_callable=AsyncMock) as mock:
        mock.return_value = "cus_test_123"
        yield mock


@pytest.fixture
def mock_checkout_params() -> Iterator[AsyncMock]:
    """Patch the payments router's checkout-params builder, defaulting to an empty parameter set."""
    with patch("app.payments.routers.payments.build_checkout_params", new_callable=AsyncMock) as mock:
        mock.return_value = {}
        yield mock


@pytest.fixture
def mock_trial_end_email() -> Iterator[MagicMock]:
    """Patch the webhook module's trial-end notification email sender."""
    with patch("app.payments.webhooks.email_service.send_trial_end_notification") as mock:
        yield mock


@pytest.fixture
def mock_webhook_construct() -> Iterator[MagicMock]:
    """Force production webhook verification and patch Stripe's event constructor (set side_effect per test)."""
    with (
        patch("app.payments.routers.payments.settings.test_mode", False),
        patch("app.payments.routers.payments.stripe.Webhook.construct_event") as mock,
    ):
        yield mock
