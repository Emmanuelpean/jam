from unittest.mock import patch

import pytest


@pytest.fixture
def mock_email_verif():
    """Patch the email-change verification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_change_verification") as mock:
        yield mock


@pytest.fixture
def mock_password_notify():
    """Patch the password-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.user.email_service.send_password_changed_notification") as mock:
        yield mock


@pytest.fixture
def mock_email_notify():
    """Patch the email-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_change_notification") as mock:
        yield mock


@pytest.fixture
def mock_release_email():
    """Patch the new-version release email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.user.email_service.send_new_version_email") as mock:
        yield mock


@pytest.fixture
def mock_verification_email():
    """Patch the email-verification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_verification_email") as mock:
        yield mock


@pytest.fixture
def mock_password_reset_email():
    """Patch the password-reset-request email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_password_reset_email") as mock:
        yield mock


@pytest.fixture
def mock_password_changed_email():
    """Patch the password-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_password_changed_notification") as mock:
        yield mock
