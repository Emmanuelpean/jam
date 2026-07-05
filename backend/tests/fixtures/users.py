"""User fixtures for testing."""

from typing import TYPE_CHECKING, cast

import pytest

from app import models
from tests.base_test import BaseTest
from tests.utils import test_data as td
from tests.utils.create_data.core import create_users

if TYPE_CHECKING:
    from starlette.testclient import TestClient


class _LazyUserClient:
    """Descriptor exposing user.client - an authorised TestClient built (and cached) on first access.
    Only resolved when accessed, so user fixtures used by DB-only tests never build a client."""

    def __get__(self, user: models.User, _owner=None):
        if user is None:
            return self
        client = user.__dict__.get("_authorised_client")
        if client is None:
            factory = user._request.getfixturevalue("authorised_client_factory")  # noqa
            client = factory(user)
            user.__dict__["_authorised_client"] = client
        return client


class FixtureUser(models.User):
    """A ``models.User`` extended with the test-only attributes and helper methods used across the suite.

    Marked ``__abstract__`` so SQLAlchemy does not map it: it is not a second table or a polymorphic
    variant, just the single place where the helpers are defined. ``_patch_user`` copies these methods
    (and the lazy ``client`` descriptor) onto ``models.User`` at import time, so every user instance -
    fixture-created, relationship-loaded, or re-queried - gains them. Fixtures return real ``models.User``
    objects annotated as ``FixtureUser`` so editors and type checkers surface the added members.

    Each helper resolves the active pytest ``session`` from ``self._request``, which the fixtures set;
    calling them on a user that did not come from a fixture raises ``AttributeError`` for ``_request``.
    """

    __abstract__ = True

    plain_password: str
    plain_verification_token: str
    client: "TestClient"

    def create_user_qualification(self, **kwargs) -> models.UserQualification:
        """Create a user qualification owned by this user. See BaseTest.create_user_qualification."""
        return BaseTest.create_user_qualification(self._request.getfixturevalue("session"), self, **kwargs)

    def create_job(self, **kwargs) -> models.Job:
        """Create a job owned by this user. See BaseTest.create_job."""
        return BaseTest.create_job(self._request.getfixturevalue("session"), self, **kwargs)

    def create_person(self, **kwargs) -> models.Person:
        """Create a person owned by this user. See BaseTest.create_person."""
        return BaseTest.create_person(self._request.getfixturevalue("session"), self, **kwargs)

    def create_company(self, **kwargs) -> models.Company:
        """Create a company owned by this user. See BaseTest.create_company."""
        return BaseTest.create_company(self._request.getfixturevalue("session"), self, **kwargs)

    def create_aggregator(self, **kwargs) -> models.Aggregator:
        """Create an aggregator owned by this user. See BaseTest.create_aggregator."""
        return BaseTest.create_aggregator(self._request.getfixturevalue("session"), self, **kwargs)

    def create_keyword(self, name: str = "Python", **kwargs) -> models.Keyword:
        """Create a keyword owned by this user. See BaseTest.create_keyword."""
        return BaseTest.create_keyword(self._request.getfixturevalue("session"), self, name, **kwargs)

    def create_interview(self, job, **kwargs) -> models.Interview:
        """Create an interview for the given job owned by this user. See BaseTest.create_interview."""
        return BaseTest.create_interview(self._request.getfixturevalue("session"), self, job, **kwargs)

    def create_job_application_update(self, job, **kwargs) -> models.JobApplicationUpdate:
        """Create a job application update for the given job owned by this user. See BaseTest.create_job_application_update."""
        return BaseTest.create_job_application_update(self._request.getfixturevalue("session"), self, job, **kwargs)

    def create_speculative_application(self, company, **kwargs) -> models.SpeculativeApplication:
        """Create a speculative application against the given company owned by this user. See BaseTest.create_speculative_application."""
        return BaseTest.create_speculative_application(
            self._request.getfixturevalue("session"), self, company, **kwargs
        )

    def create_file(self, **kwargs) -> models.File:
        """Create a file owned by this user. See BaseTest.create_file."""
        return BaseTest.create_file(self._request.getfixturevalue("session"), self, **kwargs)

    def create_forwarding_confirmation_link(self, **kwargs) -> models.ForwardingConfirmationLink:
        """Create a forwarding confirmation link owned by this user. See BaseTest.create_forwarding_confirmation_link."""
        session = self._request.getfixturevalue("session")
        return BaseTest.create_forwarding_confirmation_link(session, self, **kwargs)

    def create_scraped_job(self, service_log=None, **kwargs) -> models.ScrapedJob:
        """Create a scraped job owned by this user. See BaseTest.create_scraped_job."""
        return BaseTest.create_scraped_job(self._request.getfixturevalue("session"), self, service_log, **kwargs)

    def create_job_email(self, service_log=None, **kwargs) -> models.JobEmail:
        """Create a job alert email owned by this user. See BaseTest.create_job_email."""
        return BaseTest.create_job_email(self._request.getfixturevalue("session"), self, service_log, **kwargs)

    def create_job_rating(self, scraped_job=None, user_qualification=None, **kwargs) -> models.JobRating:
        """Create a job rating owned by this user. See BaseTest.create_job_rating."""
        session = self._request.getfixturevalue("session")
        return BaseTest.create_job_rating(session, self, scraped_job, user_qualification, **kwargs)

    def create_scraping_exclusion_filter(self, **kwargs) -> models.ScrapingExclusionFilter:
        """Create a scraping exclusion filter owned by this user. See BaseTest.create_scraping_exclusion_filter."""
        session = self._request.getfixturevalue("session")
        return BaseTest.create_scraping_exclusion_filter(session, self, **kwargs)

    def create_scraping_favourite_filter(self, **kwargs) -> models.ScrapingFavouriteFilter:
        """Create a scraping favourite filter owned by this user. See BaseTest.create_scraping_favourite_filter."""
        session = self._request.getfixturevalue("session")
        return BaseTest.create_scraping_favourite_filter(session, self, **kwargs)

    def get_token(self, token_type) -> models.UserToken | None:
        """Get the most recent token of the given type for this user. See BaseTest.get_token."""
        return BaseTest.get_token(self._request.getfixturevalue("session"), self, token_type)

    def create_token(self, token_type, **kwargs) -> tuple[str, models.UserToken]:
        """Generate a token of the given type for this user. See BaseTest.create_token."""
        return BaseTest.create_token(self._request.getfixturevalue("session"), self, token_type, **kwargs)

    def refresh(self) -> "FixtureUser":
        """Refresh this user instance from the database (session.refresh)."""
        self._request.getfixturevalue("session").refresh(self)
        return self

    def reauthenticate(self) -> "FixtureUser":
        """Refresh this user and rebuild its authorised client with a token for the current token_version.
        Use after an action that revokes existing tokens (e.g. a password change) to keep making requests."""
        self.refresh()
        self.__dict__.pop("_authorised_client", None)
        return self


def _patch_user() -> None:
    """Copy FixtureUser's helpers and the lazy client descriptor onto models.User (once)."""
    if hasattr(models.User, "create_token"):
        return
    for name, attr in vars(FixtureUser).items():
        if callable(attr) and not name.startswith("__"):
            setattr(models.User, name, attr)
    models.User.client = _LazyUserClient()


_patch_user()


def _single_user(session, request, user_data: dict) -> "FixtureUser":
    """Create and return a single user from its USER_DATA entry, wired up for lazy user.client"""

    user = create_users(session, [user_data])[0]
    user._request = request
    return cast("FixtureUser", user)


@pytest.fixture
def test_regular_user(session, request) -> "FixtureUser":
    """Fixture for a regular (non-admin, premium) user."""
    return _single_user(session, request, td.REGULAR_USER)


@pytest.fixture
def test_admin_user(session, request) -> "FixtureUser":
    """Fixture for an admin user."""
    return _single_user(session, request, td.ADMIN_USER)


@pytest.fixture
def test_demo_user(session, request) -> "FixtureUser":
    """Fixture for a demo user."""
    return _single_user(session, request, td.DEMO_USER)


@pytest.fixture
def test_inactive_user(session, request) -> "FixtureUser":
    """Fixture for an inactive user."""
    return _single_user(session, request, td.INACTIVE_USER)


@pytest.fixture
def test_unverified_user(session, request) -> "FixtureUser":
    """Fixture for an unverified user (i.e. is_verified=False)."""
    return _single_user(session, request, td.UNVERIFIED_USER)


@pytest.fixture
def test_toast_user_1(session, request) -> "FixtureUser":
    """Fixture for the first named premium user (used by the job-scraping suite)."""
    return _single_user(session, request, td.PREMIUM_USER_1)


@pytest.fixture
def test_toast_user_2(session, request) -> "FixtureUser":
    """Fixture for the second named premium user (used by the job-scraping suite)."""
    return _single_user(session, request, td.PREMIUM_USER_2)


@pytest.fixture
def test_gmail_user(session, request) -> "FixtureUser":
    """Fixture for a registered user with a gmail address (e.g. a forwarding-email originator)."""
    return _single_user(session, request, {"email": "test@gmail.com", "password": "test123"})


@pytest.fixture
def test_stripe_user(session, request) -> "FixtureUser":
    """Fixture for a user with Stripe details (used only by the payments suite)."""
    return _single_user(session, request, td.STRIPE_USER)


@pytest.fixture
def test_non_premium_user(session, request) -> "FixtureUser":
    """Fixture for a non-premium user (used only by the payments suite)."""
    return _single_user(session, request, td.NON_PREMIUM_USER)
