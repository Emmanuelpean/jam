"""HTTP-level tests for the unified service-error endpoints (/service-errors)."""

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser
from tests.utils.create_data.utils import create_db_entries


@pytest.fixture
def seeded_service_errors(session: Session) -> list[models.ServiceError]:
    """Seed a mix of acknowledged / unacknowledged errors across services."""

    scraping_log = BaseTest.create_email_scraping_service_log(session)
    rating_log = BaseTest.create_job_rating_service_log(session)
    monitoring_log = create_db_entries(session, models.ProviderMonitoringServiceLog, {})[0]

    return [
        BaseTest.create_service_error(
            session,
            error_type="RuntimeError",
            message="scrape boom",
            job_email_scraping_service_log_id=scraping_log.id,
        ),
        BaseTest.create_service_error(
            session,
            error_type="ValueError",
            message="rating boom",
            job_rating_service_log_id=rating_log.id,
        ),
        BaseTest.create_service_error(
            session,
            error_type="TimeoutError",
            message="fetch boom",
            is_acknowledged=True,
            provider_monitoring_service_log_id=monitoring_log.id,
        ),
    ]


class TestListServiceErrors(BaseTest):
    endpoint = "/service-errors/"

    def test_returns_all_newest_first(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 3
        ids = [row["id"] for row in body]
        assert ids == sorted(ids, reverse=True)

    def test_filter_by_service(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        rating_log_id = seeded_service_errors[1].job_rating_service_log_id
        resp = test_admin_user.client.get(self.endpoint, params={"job_rating_service_log_id": rating_log_id})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 1
        assert body[0]["message"] == "rating boom"

    def test_filter_by_acknowledged(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        resp = test_admin_user.client.get(self.endpoint, params={"is_acknowledged": "false"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 2
        assert all(not row["is_acknowledged"] for row in body)

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestUnacknowledgedErrorCounts(BaseTest):
    endpoint = "/service-errors/counts"

    @pytest.fixture
    def seeded_counts(self, session: Session) -> None:
        """Seed unacknowledged errors across all three services plus one acknowledged error."""

        scraping_log = BaseTest.create_email_scraping_service_log(session)
        rating_log = BaseTest.create_job_rating_service_log(session)
        monitoring_log = create_db_entries(session, models.ProviderMonitoringServiceLog, {})[0]

        BaseTest.create_service_error(session, message="scrape 1", job_email_scraping_service_log_id=scraping_log.id)
        BaseTest.create_service_error(session, message="scrape 2", job_email_scraping_service_log_id=scraping_log.id)
        BaseTest.create_service_error(session, message="rating 1", job_rating_service_log_id=rating_log.id)
        BaseTest.create_service_error(
            session,
            message="rating acknowledged",
            job_rating_service_log_id=rating_log.id,
            is_acknowledged=True,
        )
        BaseTest.create_service_error(
            session, message="monitor 1", provider_monitoring_service_log_id=monitoring_log.id
        )

    def test_counts_unacknowledged_per_service(self, seeded_counts: None, test_admin_user: FixtureUser) -> None:
        # No previous_login on the fixture user, so every unacknowledged error is counted.
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"job_email_scraping": 2, "job_rating": 1, "provider_monitoring": 1}

    def test_counts_zero_when_no_errors(self, test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"job_email_scraping": 0, "job_rating": 0, "provider_monitoring": 0}

    def test_counts_only_errors_since_previous_login(self, session: Session, test_admin_user: FixtureUser) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        test_admin_user.previous_login = now - dt.timedelta(hours=1)
        session.commit()

        scraping_log = BaseTest.create_email_scraping_service_log(session)
        BaseTest.create_service_error(
            session,
            message="before previous login",
            job_email_scraping_service_log_id=scraping_log.id,
            created_at=now - dt.timedelta(hours=2),
        )
        BaseTest.create_service_error(
            session,
            message="after previous login",
            job_email_scraping_service_log_id=scraping_log.id,
            created_at=now,
        )

        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"job_email_scraping": 1, "job_rating": 0, "provider_monitoring": 0}

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestAcknowledgeServiceErrors(BaseTest):
    endpoint = "/service-errors/acknowledge"

    def test_acknowledges_errors(
        self, session: Session, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        ids = [seeded_service_errors[0].id, seeded_service_errors[1].id]
        resp = test_admin_user.client.put(self.endpoint, json={"ids": ids, "is_acknowledged": True})
        assert resp.status_code == status.HTTP_200_OK
        assert all(row["is_acknowledged"] for row in resp.json())

        for error_id in ids:
            error = self.get_by_id(session, models.ServiceError, error_id)
            session.refresh(error)
            assert error.is_acknowledged is True

    def test_unacknowledge(
        self, session: Session, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        already_ack = seeded_service_errors[2].id
        resp = test_admin_user.client.put(self.endpoint, json={"ids": [already_ack], "is_acknowledged": False})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()[0]["is_acknowledged"] is False

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        resp = test_regular_user.client.put(self.endpoint, json={"ids": [1], "is_acknowledged": True})
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestServiceErrorFkConstraints(BaseTest):
    """The DB CHECK constraints reject inconsistent FK combinations."""

    @staticmethod
    def _add(session: Session, **fks) -> None:
        session.add(models.ServiceError(error_type="X", message="m", traceback="t", **fks))
        session.flush()

    def test_rejects_row_with_no_fk(self, session: Session) -> None:
        with pytest.raises(IntegrityError):
            with session.begin_nested():
                self._add(session)

    def test_rejects_scraped_job_without_scraping_log(self, session: Session, test_regular_user: FixtureUser) -> None:
        scraped_job = test_regular_user.create_scraped_job()
        with pytest.raises(IntegrityError):
            with session.begin_nested():
                self._add(session, scraped_job_id=scraped_job.id)

    def test_rejects_rating_without_rating_log(self, session: Session, test_regular_user: FixtureUser) -> None:
        rating = test_regular_user.create_job_rating()
        with pytest.raises(IntegrityError):
            with session.begin_nested():
                self._add(session, job_rating_id=rating.id)

    def test_rejects_two_service_logs(self, session: Session) -> None:
        scraping_log = self.create_email_scraping_service_log(session)
        rating_log = self.create_job_rating_service_log(session)
        with pytest.raises(IntegrityError):
            with session.begin_nested():
                self._add(
                    session,
                    job_email_scraping_service_log_id=scraping_log.id,
                    job_rating_service_log_id=rating_log.id,
                )

    def test_accepts_valid_per_job_scraping_error(self, session: Session, test_regular_user: FixtureUser) -> None:
        scraped_job = test_regular_user.create_scraped_job()
        self._add(
            session,
            scraped_job_id=scraped_job.id,
            job_email_scraping_service_log_id=scraped_job.service_log_id,
        )
        assert session.query(models.ServiceError).count() == 1
