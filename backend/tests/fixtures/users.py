"""User fixtures for testing."""

import datetime as dt

import pytest

from app import models
from app.utils import hash_token
from tests.utils.create_data.core import create_users, create_user_qualifications
from tests.utils import test_data as td


@pytest.fixture
def test_users(session) -> list[models.User]:
    """Create test user data"""
    return create_users(session)


@pytest.fixture
def test_admin_user(test_users) -> models.User:
    """Fixture for an admin user."""
    return test_users[td.ADMIN_USER_INDEX]


@pytest.fixture
def test_demo_user(test_users) -> models.User:
    """Fixture for a non-admin user."""
    return test_users[td.DEMO_USER_INDEX]


@pytest.fixture
def test_regular_user(test_users) -> models.User:
    """Fixture for a non-admin user."""
    return test_users[td.REGULAR_USER_INDEX]


@pytest.fixture
def test_inactive_user(test_users) -> models.User:
    """Fixture for an inactive user."""
    return test_users[td.INACTIVE_USER_INDEX]


@pytest.fixture
def test_unverified_user(test_users) -> models.User:
    """Fixture to create an unverified user (i.e. is_verified=False)."""
    return test_users[td.UNVERIFIED_USER_INDEX]


@pytest.fixture
def test_unverified_token_user(session) -> models.User:
    """Fixture to create an unverified user with a verification token."""
    plain_token = "testtoken"
    hashed_token = hash_token(plain_token)

    user_data = dict(
        email="unverified@test.com",
        password="password",
        is_verified=False,
        is_active=True,
    )

    user = create_users(session, [user_data])[0]

    # noinspection PyArgumentList
    verification_token = models.UserToken(
        owner_id=user.id,
        token=hashed_token,
        token_type="verification",
        created_at=dt.datetime.now(dt.timezone.utc),
    )
    session.add(verification_token)
    session.commit()

    user.plain_verification_token = plain_token
    return user


@pytest.fixture
def test_user_change_email_token_user(session) -> models.User:
    """Fixture to create a user with a change email token."""
    plain_token = "changeemailtoken"
    hashed_token = hash_token(plain_token)

    user_data = dict(
        email="test_user@test.com",
        password="password",
        is_verified=True,
        is_active=True,
    )

    user = create_users(session, [user_data])[0]

    # noinspection PyArgumentList
    email_change_token = models.UserToken(
        owner_id=user.id,
        token=hashed_token,
        token_type="email_change",
        created_at=dt.datetime.now(dt.timezone.utc),
        pending_email="newemail@test.com",
    )
    session.add(email_change_token)
    session.commit()

    user.plain_verification_token = plain_token
    return user


@pytest.fixture
def test_user_qualifications(session, test_users) -> list[models.UserQualification]:
    """Create test user qualifications"""
    return create_user_qualifications(session, test_users)


@pytest.fixture
def test_stripe_user(session, test_users) -> models.User:
    """Create test user data with stripe data"""
    return test_users[td.STRIPE_USER_INDEX]
