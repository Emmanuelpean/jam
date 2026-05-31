"""Tests for tour-related routes: POST /scraped-jobs/tour-demo and POST /tour/clear-all."""

import datetime as dt

from starlette import status

from app import models
from tests.utils.create_data.utils import create_db_entries


# -------------------------------------------------- HELPERS ---------------------------------------------------


def _create_tour_entities(session, user: models.User) -> dict:
    """Create a minimal set of is_tour=True entities for the given user.
    Returns a dict of created objects keyed by type."""

    now = dt.datetime.now(dt.timezone.utc)

    service_log = create_db_entries(
        session,
        models.JobEmailScrapingServiceLog,
        {"run_datetime": now, "is_tour": True},
    )[0]

    email = create_db_entries(
        session,
        models.JobEmail,
        {
            "owner_id": user.id,
            "service_log_id": service_log.id,
            "external_email_id": "tour-test-email",
            "subject": "Tour email",
            "body": "body",
            "platform": "linkedin",
            "sender": "test@test.com",
            "date_received": now,
            "is_tour": True,
        },
    )[0]

    scraped_job = create_db_entries(
        session,
        models.ScrapedJob,
        {
            "owner_id": user.id,
            "service_log_id": service_log.id,
            "external_job_id": f"tour-test-{user.id}",
            "platform": "LinkedIn",
            "is_processed": True,
            "is_scraped": True,
            "scrape_datetime": now,
            "is_active": True,
            "is_tour": True,
            "title": "Tour Job",
        },
    )[0]

    user_qualification = create_db_entries(
        session,
        models.UserQualification,
        {"owner_id": user.id, "is_tour": True, "experience": "tour experience"},
    )[0]

    job_rating = create_db_entries(
        session,
        models.JobRating,
        {
            "owner_id": user.id,
            "scraped_job_id": scraped_job.id,
            "user_qualification_id": user_qualification.id,
            "llm_model": "tour-demo",
            "is_success": True,
            "overall_score": 8,
            "is_tour": True,
        },
    )[0]

    company = create_db_entries(
        session,
        models.Company,
        {"owner_id": user.id, "name": f"Tour Company {user.id}", "is_tour": True},
    )[0]

    keyword = create_db_entries(
        session,
        models.Keyword,
        {"owner_id": user.id, "name": f"tour-keyword-{user.id}", "is_tour": True},
    )[0]

    job = create_db_entries(
        session,
        models.Job,
        {"owner_id": user.id, "title": "Tour Job", "company_id": company.id, "is_tour": True},
    )[0]

    job_application_update = create_db_entries(
        session,
        models.JobApplicationUpdate,
        {"owner_id": user.id, "job_id": job.id, "type": "received", "is_tour": True},
    )[0]

    speculative_application = create_db_entries(
        session,
        models.SpeculativeApplication,
        {"owner_id": user.id, "company_id": company.id, "is_tour": True},
    )[0]

    file = create_db_entries(
        session,
        models.File,
        {
            "owner_id": user.id,
            "filename": "tour-cv.pdf",
            "content": "base64content",
            "type": "application/pdf",
            "size": 1024,
            "is_tour": True,
        },
    )[0]

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


def _create_non_tour_entities(session, user: models.User) -> dict:
    """Create is_tour=False entities to verify they survive clear-all."""

    now = dt.datetime.now(dt.timezone.utc)

    service_log = create_db_entries(
        session,
        models.JobEmailScrapingServiceLog,
        {"run_datetime": now, "is_tour": False},
    )[0]

    scraped_job = create_db_entries(
        session,
        models.ScrapedJob,
        {
            "owner_id": user.id,
            "service_log_id": service_log.id,
            "external_job_id": f"real-job-{user.id}",
            "platform": "LinkedIn",
            "is_processed": True,
            "is_scraped": True,
            "scrape_datetime": now,
            "is_active": True,
            "is_tour": False,
            "title": "Real Job",
        },
    )[0]

    company = create_db_entries(
        session,
        models.Company,
        {"owner_id": user.id, "name": f"Real Company {user.id}", "is_tour": False},
    )[0]

    return {"scraped_job": scraped_job, "company": company}


# ----------------------------------------------- TOUR DEMO -------------------------------------------------------


class TestCreateTourDemo:
    """Tests for POST /scraped-jobs/tour-demo"""

    endpoint = "/scraped-jobs/tour-demo"

    def test_creates_scraped_job_with_tour_data(self, regular_user_client, test_regular_user, session) -> None:
        """Should return a ScrapedJob and create linked JobEmail, UserQualification, and JobRating."""

        response = regular_user_client.post(self.endpoint)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_tour"] is True
        assert data["owner_id"] == test_regular_user.id
        assert len(data["emails"]) == 1

        scraped_job_id = data["id"]
        email_id = data["emails"][0]

        # Verify DB state
        scraped_job = session.query(models.ScrapedJob).filter_by(id=scraped_job_id).first()
        assert scraped_job is not None
        assert scraped_job.is_tour is True

        email = session.query(models.JobEmail).filter_by(id=email_id).first()
        assert email is not None
        assert email.is_tour is True

        rating = session.query(models.JobRating).filter_by(scraped_job_id=scraped_job_id).first()
        assert rating is not None
        assert rating.is_tour is True

        qual = session.query(models.UserQualification).filter_by(id=rating.user_qualification_id).first()
        assert qual is not None
        assert qual.is_tour is True

    def test_unauthenticated(self, client) -> None:
        """Should return 401 for unauthenticated requests."""

        response = client.post(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------- CLEAR ALL -------------------------------------------------------


class TestClearAllTourData:
    """Tests for POST /tour/clear-all"""

    endpoint = "/tour/clear-all"

    def test_deletes_all_tour_entities_for_user(self, regular_user_client, test_regular_user, session) -> None:
        """Should delete all is_tour=True rows owned by the current user."""

        _create_tour_entities(session, test_regular_user)
        uid = test_regular_user.id

        response = regular_user_client.post(self.endpoint)

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

    def test_does_not_delete_non_tour_entities(self, regular_user_client, test_regular_user, session) -> None:
        """Should leave is_tour=False rows untouched."""

        non_tour = _create_non_tour_entities(session, test_regular_user)
        uid = test_regular_user.id

        regular_user_client.post(self.endpoint)
        session.expire_all()

        assert session.query(models.ScrapedJob).filter_by(id=non_tour["scraped_job"].id).first() is not None
        assert session.query(models.Company).filter_by(id=non_tour["company"].id).first() is not None
        assert session.query(models.ScrapedJob).filter_by(owner_id=uid, is_tour=False).count() == 1

    def test_does_not_delete_another_users_tour_data(self, regular_user_client, test_admin_user, session) -> None:
        """Should only delete tour data belonging to the authenticated user."""

        admin_entities = _create_tour_entities(session, test_admin_user)

        regular_user_client.post(self.endpoint)
        session.expire_all()

        assert session.query(models.ScrapedJob).filter_by(id=admin_entities["scraped_job"].id).first() is not None
        assert session.query(models.JobEmail).filter_by(id=admin_entities["email"].id).first() is not None

    def test_idempotent_when_no_tour_data(self, regular_user_client) -> None:
        """Should return 204 even when there is nothing to delete."""

        response = regular_user_client.post(self.endpoint)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unauthenticated(self, client) -> None:
        """Should return 401 for unauthenticated requests."""

        response = client.post(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
