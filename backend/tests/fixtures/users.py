"""User fixtures for testing."""

import uuid
from typing import TYPE_CHECKING, cast
import datetime as dt

import pytest

from app import models
from core.utils import generate_token
from fixtures.database import session
from tests.base_test import BaseTest
from tests.utils import test_data as td
from tests.utils.create_data.core import create_users
from utils.create_data.utils import create_db_entries

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
        session = self._request.getfixturevalue("session")
        return create_db_entries(session, models.UserQualification, {"owner_id": self.id, **kwargs})[0]

    def create_job(self, **kwargs) -> models.Job:
        """Create a job owned by this user. See BaseTest.create_job."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "title": "Test Job", **kwargs}
        return create_db_entries(session, models.Job, data)[0]

    def create_person(self, **kwargs) -> models.Person:
        """Create a person owned by this user. See BaseTest.create_person."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "first_name": "John", "last_name": "Doe", **kwargs}
        return create_db_entries(session, models.Person, data)[0]

    def create_company(self, **kwargs) -> models.Company:
        """Create a company owned by this user. See BaseTest.create_company."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "name": "Acme Corp", **kwargs}
        return create_db_entries(session, models.Company, data)[0]

    def create_aggregator(self, **kwargs) -> models.Aggregator:
        """Create an aggregator owned by this user. See BaseTest.create_aggregator."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "name": "LinkedIn", "url": "https://linkedin.com", **kwargs}
        return create_db_entries(session, models.Aggregator, data)[0]

    def create_keyword(self, name: str = "Python", **kwargs) -> models.Keyword:
        """Create a keyword owned by this user. See BaseTest.create_keyword."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "name": name, **kwargs}
        return create_db_entries(session, models.Keyword, data)[0]

    def create_interview(self, job: models.Job, **kwargs) -> models.Interview:
        """Create an interview for the given job owned by this user. See BaseTest.create_interview."""

        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "job_id": job.id, "type": "technical", **kwargs}
        return create_db_entries(session, models.Interview, data)[0]

    def create_job_application_update(self, job: models.Job, **kwargs) -> models.JobApplicationUpdate:
        """Create a job application update for the given job owned by this user. See BaseTest.create_job_application_update."""

        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "job_id": job.id, "type": "received", **kwargs}
        return create_db_entries(session, models.JobApplicationUpdate, data)[0]

    def create_speculative_application(self, company: models.Company, **kwargs) -> models.SpeculativeApplication:
        """Create a speculative application against the given company owned by this user. See BaseTest.create_speculative_application."""

        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "company_id": company.id, **kwargs}
        return create_db_entries(session, models.SpeculativeApplication, data)[0]

    def create_file(self, **kwargs) -> models.File:
        """Create a file owned by this user. See BaseTest.create_file."""

        session = self._request.getfixturevalue("session")
        data = {
            "owner_id": self.id,
            "filename": "cv.pdf",
            "content": "base64content",
            "type": "application/pdf",
            "size": 1024,
            **kwargs,
        }
        return create_db_entries(session, models.File, data)[0]

    def create_forwarding_confirmation_link(self, **kwargs) -> models.ForwardingConfirmationLink:
        """Create a forwarding confirmation link owned by this user. See BaseTest.create_forwarding_confirmation_link."""

        session = self._request.getfixturevalue("session")
        data = {
            "owner_id": self.id,
            "email_external_id": "ext_123",
            "url": "https://example.com/confirm",
            "platform": "gmail",
            **kwargs,
        }
        return create_db_entries(session, models.ForwardingConfirmationLink, data)[0]

    def create_scraped_job(
        self,
        service_log: models.JobEmailScrapingServiceLog | None = None,
        **kwargs,
    ) -> models.ScrapedJob:
        """Create a scraped job owned by this user. See BaseTest.create_scraped_job."""

        session = self._request.getfixturevalue("session")
        if service_log is None:
            service_log = BaseTest.create_email_scraping_service_log(session)
        data = {
            "owner_id": self.id,
            "service_log_id": service_log.id,
            "external_job_id": str(uuid.uuid4()),
            "platform": "linkedin",
            **kwargs,
        }
        return create_db_entries(session, models.ScrapedJob, data)[0]

    def create_job_email(
        self,
        service_log: models.JobEmailScrapingServiceLog | None = None,
        **kwargs,
    ) -> models.JobEmail:
        """Create a job alert email owned by this user. See BaseTest.create_job_email."""

        session = self._request.getfixturevalue("session")
        if service_log is None:
            service_log = BaseTest.create_email_scraping_service_log(session)
        data = {
            "owner_id": self.id,
            "service_log_id": service_log.id,
            "external_email_id": str(uuid.uuid4()),
            "subject": "Test Job Alert",
            "sender": "jobs@linkedin.com",
            "date_received": dt.datetime.now(dt.timezone.utc),
            "platform": "linkedin",
            "body": "Test email body",
            **kwargs,
        }
        return create_db_entries(session, models.JobEmail, data)[0]

    def create_job_rating(
        self,
        scraped_job: models.ScrapedJob | None = None,
        user_qualification: models.UserQualification | None = None,
        **kwargs,
    ) -> models.JobRating:
        """Create a job rating owned by this user. See BaseTest.create_job_rating."""
        session = self._request.getfixturevalue("session")
        if scraped_job is None:
            scraped_job = self.create_scraped_job()
        if user_qualification is None:
            user_qualification = self.create_user_qualification(experience="Test")
        data = {
            "owner_id": self.id,
            "scraped_job_id": scraped_job.id,
            "user_qualification_id": user_qualification.id,
            "llm_model": "claude",
            **kwargs,
        }
        return create_db_entries(session, models.JobRating, data)[0]

    def create_scraping_exclusion_filter(self, **kwargs) -> models.ScrapingExclusionFilter:
        """Create a scraping exclusion filter owned by this user. See BaseTest.create_scraping_exclusion_filter."""

        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "type": "title", "operator": "contains", "value": "Some", **kwargs}
        return create_db_entries(session, models.ScrapingExclusionFilter, data)[0]

    def create_scraping_favourite_filter(self, **kwargs) -> models.ScrapingFavouriteFilter:
        """Create a scraping favourite filter owned by this user. See BaseTest.create_scraping_favourite_filter."""
        session = self._request.getfixturevalue("session")
        data = {"owner_id": self.id, "type": "title", "operator": "contains", "value": "Python", **kwargs}
        return create_db_entries(session, models.ScrapingFavouriteFilter, data)[0]

    def get_token(self, token_type) -> models.UserToken | None:
        """Get the most recent token of the given type for this user. See BaseTest.get_token."""

        session = self._request.getfixturevalue("session")
        return (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == self.id)
            .filter(models.UserToken.token_type == token_type)
            .order_by(models.UserToken.created_at.desc())
            .first()
        )

    def create_token(self, token_type, **kwargs) -> tuple[str, models.UserToken]:
        """Generate a token of the given type for this user. See BaseTest.create_token."""

        session = self._request.getfixturevalue("session")
        return generate_token(self.id, token_type, session, **kwargs)

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
