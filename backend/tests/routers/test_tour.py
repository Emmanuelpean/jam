"""Tests for tour-related routes: POST /scraped-jobs/tour-demo and POST /tour/clear-all."""

from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from base_models import ProcessingStatus
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser

# -------------------------------------------------- HELPERS ---------------------------------------------------


def _create_tour_entities(user: FixtureUser, session: Session) -> dict:
    """Create a minimal set of is_tour=True entities for the given user.
    Returns a dict of created objects keyed by type."""

    service_log = BaseTest.create_email_scraping_service_log(session, is_tour=True)
    email = user.create_job_email(service_log=service_log, is_tour=True)
    scraped_job = user.create_scraped_job(
        service_log=service_log, status=ProcessingStatus.COMPLETED, title="Tour Job", is_tour=True
    )
    user_qualification = user.create_user_qualification(experience="tour experience", is_tour=True)
    job_rating = user.create_job_rating(
        scraped_job=scraped_job,
        user_qualification=user_qualification,
        llm_model="tour-demo",
        status=ProcessingStatus.COMPLETED,
        overall_score=8,
        is_tour=True,
    )
    company = user.create_company(name=f"Tour Company {user.id}", is_tour=True)
    keyword = user.create_keyword(name=f"tour-keyword-{user.id}", is_tour=True)
    job = user.create_job(title="Tour Job", company_id=company.id, is_tour=True)
    job_application_update = user.create_job_application_update(job, type="received", is_tour=True)
    speculative_application = user.create_speculative_application(company, is_tour=True)
    file = user.create_file(is_tour=True)

    return {
        "service_log": service_log,
        "email": email,
        "scraped_job": scraped_job,
        "user_qualification": user_qualification,
        "job_rating": job_rating,
        "company": company,
        "keyword": keyword,
        "job": job,
        "job_application_update": job_application_update,
        "speculative_application": speculative_application,
        "file": file,
    }


def _create_non_tour_entities(user: FixtureUser) -> dict:
    """Create is_tour=False entities to verify they survive clear-all."""

    scraped_job = user.create_scraped_job(status=ProcessingStatus.COMPLETED, title="Real Job", is_tour=False)
    company = user.create_company(name=f"Real Company {user.id}", is_tour=False)
    return {"scraped_job": scraped_job, "company": company}


# ----------------------------------------------- TOUR DEMO -------------------------------------------------------


class TestCreateTourDemo(BaseTest):
    """Tests for POST /scraped-jobs/tour-demo"""

    endpoint = "/scraped-jobs/tour-demo"

    def test_creates_scraped_job_with_tour_data(self, test_regular_user: FixtureUser, session: Session) -> None:
        """Should return a ScrapedJob and create linked JobEmail, UserQualification, and JobRating."""

        response = test_regular_user.client.post(self.endpoint)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_tour"] is True
        assert data["owner_id"] == test_regular_user.id
        assert len(data["emails"]) == 1

        scraped_job_id = data["id"]
        email_id = data["emails"][0]

        # Verify DB state
        scraped_job = self.get_by_id(session, models.ScrapedJob, scraped_job_id)
        assert scraped_job is not None
        assert scraped_job.is_tour is True

        email = self.get_by_id(session, models.JobEmail, email_id)
        assert email is not None
        assert email.is_tour is True

        rating = session.query(models.JobRating).filter_by(scraped_job_id=scraped_job_id).first()
        assert rating is not None
        assert rating.is_tour is True

        qual = self.get_by_id(session, models.UserQualification, rating.user_qualification_id)
        assert qual is not None
        assert qual.is_tour is True

    def test_unauthenticated(self, client: TestClient) -> None:
        """Should return 401 for unauthenticated requests."""

        response = client.post(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------- CLEAR ALL -------------------------------------------------------


class TestClearAllTourData(BaseTest):
    """Tests for POST /tour/clear-all"""

    endpoint = "/tour/clear-all"

    def test_deletes_all_tour_entities_for_user(self, test_regular_user: FixtureUser, session: Session) -> None:
        """Should delete all is_tour=True rows owned by the current user."""

        _create_tour_entities(test_regular_user, session)
        uid = test_regular_user.id

        response = test_regular_user.client.post(self.endpoint)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        session.expire_all()

        assert session.query(models.ScrapedJob).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.JobEmail).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.UserQualification).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.Company).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.Keyword).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.Job).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.JobApplicationUpdate).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.SpeculativeApplication).filter_by(owner_id=uid, is_tour=True).count() == 0
        assert session.query(models.File).filter_by(owner_id=uid, is_tour=True).count() == 0

    def test_does_not_delete_non_tour_entities(self, test_regular_user: FixtureUser, session: Session) -> None:
        """Should leave is_tour=False rows untouched."""

        non_tour = _create_non_tour_entities(test_regular_user)
        uid = test_regular_user.id

        test_regular_user.client.post(self.endpoint)
        session.expire_all()

        assert session.query(models.ScrapedJob).filter_by(id=non_tour["scraped_job"].id).first() is not None
        assert session.query(models.Company).filter_by(id=non_tour["company"].id).first() is not None
        assert session.query(models.ScrapedJob).filter_by(owner_id=uid, is_tour=False).count() == 1

    def test_does_not_delete_another_users_tour_data(
        self, test_admin_user: FixtureUser, session: Session, test_regular_user: FixtureUser
    ) -> None:
        """Should only delete tour data belonging to the authenticated user."""

        admin_entities = _create_tour_entities(test_admin_user, session)

        test_regular_user.client.post(self.endpoint)
        session.expire_all()

        assert self.get_by_id(session, models.ScrapedJob, admin_entities["scraped_job"].id) is not None
        assert self.get_by_id(session, models.JobEmail, admin_entities["email"].id) is not None

    def test_idempotent_when_no_tour_data(self, test_regular_user: FixtureUser) -> None:
        """Should return 204 even when there is nothing to delete."""

        response = test_regular_user.client.post(self.endpoint)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unauthenticated(self, client: TestClient) -> None:
        """Should return 401 for unauthenticated requests."""

        response = client.post(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
