"""Tests for Job Scraping routers."""

import datetime as dt
import json

import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from app.job_email_scraping import schemas
from app.base_models import ProcessingStatus
from tests.base_test import BaseTest
from tests.conftest import CRUDTestBase, make_undefined_method_params
from tests.fixtures.users import FixtureUser


class TestScrapedJobsByEmail(BaseTest):
    """Test suite for GET /scraped-jobs/by-email/{email_id}"""

    endpoint = "/scraped-jobs/by-email"

    def test_get_scraped_jobs_for_email(self, test_regular_user: FixtureUser) -> None:
        """Should return scraped jobs linked to an email owned by the user"""

        jobs = [test_regular_user.create_scraped_job() for _ in range(3)]
        email = test_regular_user.create_job_email(jobs=jobs)

        response = test_regular_user.client.get(f"{self.endpoint}/{email.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(jobs)
        self.check_output(jobs, data, schemas.ScrapedJobOut)

    def test_get_scraped_jobs_for_email_with_few_jobs(self, test_admin_user: FixtureUser) -> None:
        """Should return correct number of scraped jobs for an email with fewer links"""

        jobs = [test_admin_user.create_scraped_job() for _ in range(2)]
        email = test_admin_user.create_job_email(jobs=jobs)

        response = test_admin_user.client.get(f"{self.endpoint}/{email.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(jobs)

    def test_not_found_nonexistent_email(self, test_regular_user: FixtureUser) -> None:
        """Should return 404 when email doesn't exist"""

        response = test_regular_user.client.get(f"{self.endpoint}/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_other_users_email(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should return 404 when email belongs to another user"""

        admin_email = test_admin_user.create_job_email()
        response = test_regular_user.client.get(f"{self.endpoint}/{admin_email.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated(self, client: TestClient, test_regular_user: FixtureUser) -> None:
        """Should return 401 when not authenticated"""

        email = test_regular_user.create_job_email()
        response = client.get(f"{self.endpoint}/{email.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestScrapedJobCRUDRegularUser(CRUDTestBase[models.ScrapedJob]):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    update_data = {"is_imported": True}
    actions_to_test = ["put"]

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.ScrapedJob:
        return owner.create_scraped_job(**overrides)

    @staticmethod
    def _seed_scraped_jobs(user: FixtureUser, total: int = 50, past_deadline: int = 3) -> None:
        """Create `total` active, un-imported scraped jobs for the user, `past_deadline` of which have a
        deadline in the past (so they are filtered out unless show_past_deadline is set)."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)
        for _ in range(total - past_deadline):
            user.create_scraped_job()
        for _ in range(past_deadline):
            user.create_scraped_job(deadline=past)

    def test_get_all(self, authorised_user: FixtureUser) -> None:
        """Test retrieving all scraped jobs for the authorised user that are scraped, not imported, active"""

        self._seed_scraped_jobs(authorised_user)
        client = authorised_user.client
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5&show_past_deadline=true")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 50
        assert len(scraped_jobs["items"]) == 5

    def test_get_all_no_past_deadlines(self, authorised_user: FixtureUser) -> None:
        """Test retrieving all scraped jobs for the authorised user that are scraped, not imported, active"""

        self._seed_scraped_jobs(authorised_user)
        client = authorised_user.client
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 50
        assert scraped_jobs["total_filtered"] == 47
        assert len(scraped_jobs["items"]) == 5

    def test_since_last_login_filters_jobs_before_previous_login(
        self, session: Session, test_regular_user: FixtureUser
    ) -> None:
        """Jobs created before previous_login are excluded when since_last_login=True."""

        previous_login = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)
        test_regular_user.previous_login = previous_login
        session.commit()

        test_regular_user.create_scraped_job(created_at=previous_login - dt.timedelta(days=1))
        test_regular_user.create_scraped_job(created_at=previous_login + dt.timedelta(hours=1))
        test_regular_user.create_scraped_job(created_at=previous_login + dt.timedelta(days=1))

        response = test_regular_user.client.get(self.endpoint + "/paged", params={"since_last_login": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 3
        assert response.json()["total_filtered"] == 2

    def test_since_last_login_no_previous_login_returns_all_jobs(
        self, session: Session, test_regular_user: FixtureUser
    ) -> None:
        """All jobs are returned when since_last_login=True but the user has no previous_login."""

        test_regular_user.previous_login = None
        session.commit()

        now = dt.datetime.now(dt.timezone.utc)
        test_regular_user.create_scraped_job(created_at=now - dt.timedelta(days=10))
        test_regular_user.create_scraped_job(created_at=now - dt.timedelta(days=5))
        test_regular_user.create_scraped_job(created_at=now)

        response = test_regular_user.client.get(self.endpoint + "/paged", params={"since_last_login": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 3

    def test_get_all_ids_only(self, authorised_user: FixtureUser) -> None:
        """Test ids_only=true returns just a list of integer IDs instead of full objects"""

        self._seed_scraped_jobs(authorised_user)
        client = authorised_user.client
        response = client.get(self.endpoint + "/paged/?page=0&page_size=10&show_past_deadline=true&ids_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 50
        assert len(data["items"]) == 10
        assert all(isinstance(item, int) for item in data["items"])


class TestPagedFilters:
    """Tests for the JSON `filters` query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    # --------------------------------------------------- TEXT FILTER --------------------------------------------------

    def test_text_filter_on_title(self, test_regular_user: FixtureUser) -> None:
        """Text filter should match title via case-insensitive substring."""

        test_regular_user.create_scraped_job(title="Senior Python Developer")
        test_regular_user.create_scraped_job(title="Junior Java Developer")
        test_regular_user.create_scraped_job(title="Data Scientist")

        filters = json.dumps({"title": {"type": "text", "value": "python"}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Senior Python Developer"

    def test_text_filter_on_company(self, test_regular_user: FixtureUser) -> None:
        """Text filter should match company name."""

        test_regular_user.create_scraped_job(title="A", company="Acme Corp")
        test_regular_user.create_scraped_job(title="B", company="Beta Inc")

        filters = json.dumps({"company": {"type": "text", "value": "acme"}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["company"] == "Acme Corp"

    # -------------------------------------------------- SELECT FILTER -------------------------------------------------

    def test_select_filter_on_platform(self, test_regular_user: FixtureUser) -> None:
        """Select filter should match exact platform values."""

        test_regular_user.create_scraped_job(title="A", platform="linkedin")
        test_regular_user.create_scraped_job(title="B", platform="indeed")
        test_regular_user.create_scraped_job(title="C", platform="nhs")

        filters = json.dumps({"platform": {"type": "select", "selected": ["indeed", "nhs"]}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        platforms = {item["platform"] for item in data["items"]}
        assert platforms == {"indeed", "nhs"}

    # -------------------------------------------------- NUMBER FILTER -------------------------------------------------

    def test_number_filter_min_on_salary(self, test_regular_user: FixtureUser) -> None:
        """Number filter with min should return jobs with salary_min >= value."""

        test_regular_user.create_scraped_job(title="Low", salary_min=20000)
        test_regular_user.create_scraped_job(title="Mid", salary_min=50000)
        test_regular_user.create_scraped_job(title="High", salary_min=80000)

        filters = json.dumps({"salary_min": {"type": "number", "min": 45000, "max": None}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Mid", "High"}

    def test_number_filter_range(self, test_regular_user: FixtureUser) -> None:
        """Number filter with both min and max should return jobs in range."""

        test_regular_user.create_scraped_job(title="Low", salary_min=20000)
        test_regular_user.create_scraped_job(title="Mid", salary_min=50000)
        test_regular_user.create_scraped_job(title="High", salary_min=80000)

        filters = json.dumps({"salary_min": {"type": "number", "min": 30000, "max": 60000}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["title"] == "Mid"

    # --------------------------------------------- NUMBER FILTER + SCORES ---------------------------------------------

    def test_number_filter_on_overall_score(self, test_regular_user: FixtureUser) -> None:
        """Number filter on job_rating.overall_score should filter via the related JobRating."""

        job_a = test_regular_user.create_scraped_job(title="Scored3")
        test_regular_user.create_job_rating(scraped_job=job_a, overall_score=3)

        job_b = test_regular_user.create_scraped_job(title="Scored7")
        test_regular_user.create_job_rating(scraped_job=job_b, overall_score=7)

        job_c = test_regular_user.create_scraped_job(title="Scored9")
        test_regular_user.create_job_rating(scraped_job=job_c, overall_score=9)

        filters = json.dumps({"job_rating.overall_score": {"type": "number", "min": 5, "max": 8}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Scored7"

    # ---------------------------------------------- NULL FILTER (nullFilter) -------------------------------------------

    def test_null_filter_not_null_excludes_unscored(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='not_null' should exclude jobs without a score."""

        job_a = test_regular_user.create_scraped_job(title="HasScore")
        test_regular_user.create_job_rating(scraped_job=job_a, overall_score=5)
        test_regular_user.create_scraped_job(title="NoScore")

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}}
        )
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "HasScore"

    def test_null_filter_null_shows_only_unscored(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='null' should show only jobs without a score."""

        job_a = test_regular_user.create_scraped_job(title="HasScore")
        test_regular_user.create_job_rating(scraped_job=job_a, overall_score=5)
        test_regular_user.create_scraped_job(title="NoScore")

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "null"}}
        )
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "NoScore"

    def test_null_filter_all_returns_everything(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='all' (or absent) should not filter on nullability."""

        job_a = test_regular_user.create_scraped_job(title="HasScore")
        test_regular_user.create_job_rating(scraped_job=job_a, overall_score=5)
        test_regular_user.create_scraped_job(title="NoScore")

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "all"}}
        )
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 2

    def test_null_filter_not_null_combined_with_range(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='not_null' combined with a range should apply both constraints."""

        job_a = test_regular_user.create_scraped_job(title="Score3")
        test_regular_user.create_job_rating(scraped_job=job_a, overall_score=3)

        job_b = test_regular_user.create_scraped_job(title="Score7")
        test_regular_user.create_job_rating(scraped_job=job_b, overall_score=7)

        test_regular_user.create_scraped_job(title="NoScore")

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": 5, "max": None, "nullFilter": "not_null"}}
        )
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Score7"

    # --------------------------------------------------- DATE FILTER --------------------------------------------------

    def test_date_filter_from(self, test_regular_user: FixtureUser) -> None:
        """Date filter with 'from' should exclude jobs with deadline before the date."""

        test_regular_user.create_scraped_job(
            title="Past",
            deadline=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )
        test_regular_user.create_scraped_job(
            title="Future",
            deadline=dt.datetime(2099, 6, 15, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"deadline": {"type": "date", "from": "2025-01-01", "to": None}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Future"

    def test_date_filter_range(self, test_regular_user: FixtureUser) -> None:
        """Date filter with from and to should return jobs within the range."""

        test_regular_user.create_scraped_job(
            title="Early",
            deadline=dt.datetime(2025, 3, 1, tzinfo=dt.timezone.utc),
        )
        test_regular_user.create_scraped_job(
            title="Mid",
            deadline=dt.datetime(2025, 3, 15, tzinfo=dt.timezone.utc),
        )
        test_regular_user.create_scraped_job(
            title="Late",
            deadline=dt.datetime(2025, 4, 10, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"deadline": {"type": "date", "from": "2025-03-10", "to": "2025-03-31"}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Mid"

    # -------------------------------------------- MULTIPLE FILTERS COMBINED -------------------------------------------

    def test_multiple_filters_combined(self, test_regular_user: FixtureUser) -> None:
        """Multiple filters should be combined with AND logic."""

        test_regular_user.create_scraped_job(
            title="Python at Acme",
            company="Acme",
            platform="linkedin",
        )
        test_regular_user.create_scraped_job(
            title="Python at Beta",
            company="Beta",
            platform="indeed",
        )
        test_regular_user.create_scraped_job(
            title="Java at Acme",
            company="Acme",
            platform="linkedin",
        )

        filters = json.dumps(
            {
                "title": {"type": "text", "value": "python"},
                "platform": {"type": "select", "selected": ["linkedin"]},
            }
        )
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python at Acme"

    # ------------------------------------------- EMPTY / INVALID FILTERS ----------------------------------------------

    def test_empty_filters_returns_all(self, test_regular_user: FixtureUser) -> None:
        """Empty filters JSON should return all jobs (no filtering)."""

        test_regular_user.create_scraped_job(title="Job1")
        test_regular_user.create_scraped_job(title="Job2")

        response = test_regular_user.client.get(
            self.endpoint, params={"filters": json.dumps({}), "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 2

    def test_no_filters_param_returns_all(self, test_regular_user: FixtureUser) -> None:
        """Omitting the filters param entirely should return all jobs."""

        test_regular_user.create_scraped_job(title="Job1")

        response = test_regular_user.client.get(self.endpoint, params={"show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1

    def test_filter_on_unknown_column_is_ignored(self, test_regular_user: FixtureUser) -> None:
        """Filters referencing non-existent columns should be silently ignored."""

        test_regular_user.create_scraped_job(title="Job1")

        filters = json.dumps({"nonexistent_column": {"type": "text", "value": "test"}})
        response = test_regular_user.client.get(
            self.endpoint, params={"filters": filters, "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1


class TestFavouritesOnly:
    """Tests for the favourites_only query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    def test_no_active_filters_returns_empty(self, test_regular_user: FixtureUser) -> None:
        """favourites_only=True with no active favourite filters should return an empty result set."""

        test_regular_user.create_scraped_job(title="Any Job")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0
        assert data["items"] == []

    def test_matching_filter_returns_only_matched_jobs(self, test_regular_user: FixtureUser) -> None:
        """favourites_only=True should return only jobs matching an active favourite filter."""

        test_regular_user.create_scraped_job(title="Python Engineer")
        test_regular_user.create_scraped_job(title="Java Developer")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python Engineer"

    def test_multiple_filters_use_or_logic(self, test_regular_user: FixtureUser) -> None:
        """Multiple active favourite filters should be combined with OR — a job matching any one is included."""

        test_regular_user.create_scraped_job(title="Python Engineer")
        test_regular_user.create_scraped_job(title="Data Scientist")
        test_regular_user.create_scraped_job(title="Java Developer")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Data")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Python Engineer", "Data Scientist"}

    def test_inactive_filters_are_ignored(self, test_regular_user: FixtureUser) -> None:
        """Inactive favourite filters should not be applied, resulting in an empty set."""

        test_regular_user.create_scraped_job(title="Python Engineer")
        test_regular_user.create_scraping_favourite_filter(
            type="title", operator="contains", value="Python", is_active=False
        )

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_false_does_not_apply_favourite_filtering(self, test_regular_user: FixtureUser) -> None:
        """favourites_only=False should return all eligible jobs, ignoring favourite filters."""

        test_regular_user.create_scraped_job(title="Python Engineer")
        test_regular_user.create_scraped_job(title="Java Developer")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "false", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2

    def test_does_not_return_other_users_jobs(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        """Jobs belonging to another user are never returned, even if a filter would match."""

        test_admin_user.create_scraped_job(title="Python Engineer")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_other_users_filters_do_not_apply(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        """Favourite filters belonging to another user should not be applied."""

        test_regular_user.create_scraped_job(title="Python Engineer")
        test_admin_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_base_filters_still_applied(self, test_regular_user: FixtureUser) -> None:
        """Imported and inactive jobs should be excluded even when they match a favourite filter."""

        test_regular_user.create_scraped_job(title="Python Imported", is_imported=True)
        test_regular_user.create_scraped_job(title="Python Inactive", is_active=False)
        test_regular_user.create_scraped_job(title="Python Active")
        test_regular_user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python Active"

    def test_company_filter(self, test_regular_user: FixtureUser) -> None:
        """Favourite filter on the company field should match correctly."""

        test_regular_user.create_scraped_job(title="Engineer", company="Acme Corp")
        test_regular_user.create_scraped_job(title="Engineer", company="Beta Ltd")
        test_regular_user.create_scraping_favourite_filter(type="company", operator="contains", value="Acme")

        response = test_regular_user.client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["company"] == "Acme Corp"

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        """Unauthenticated request should return 401."""

        response = client.get(self.endpoint, params={"favourites_only": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestScrapedJobCRUDAdminUser(CRUDTestBase[models.ScrapedJob]):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    actions_to_test = ["get_all"]
    admin_only = True

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.ScrapedJob:
        return owner.create_scraped_job(**overrides)


class TestScrapedJobRegularUserUndefinedMethods:
    ENDPOINT = "/scraped-jobs"
    DEFINED_ACTIONS = ["PUT", "GET_ALL", "POST", "DELETE"]
    UNDEFINED_ACTIONS = ["GET_ONE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(
        self,
        http_method,
        path_suffix,
        expected_status,
        test_admin_user: FixtureUser,
        test_regular_user: FixtureUser,
    ):
        response = test_admin_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = test_regular_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status


class TestPlatformStats:

    endpoint = "/scraped-jobs/platform-stats"

    def test_basic_counts(self, test_regular_user: FixtureUser) -> None:
        """Counts scraped, imported, and applied correctly."""

        sj1, sj2, sj3 = (test_regular_user.create_scraped_job() for _ in range(3))
        test_regular_user.create_job_email(platform="linkedin", alert_name="backend", jobs=[sj1, sj2, sj3])

        # 2 imported (sj1, sj2), 1 applied (sj1)
        test_regular_user.create_job(scraped_job_id=sj1.id)
        test_regular_user.create_job(scraped_job_id=sj2.id)
        test_regular_user.create_job(scraped_job_id=sj1.id, application_status="applied")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        expected = {
            "platform": "linkedin",
            "alert_name": "backend",
            "scraped_count": 3,
            "imported_count": 2,
            "applied_count": 1,
        }
        assert data[0] == expected

    def test_multiple_platforms_and_alerts(self, test_regular_user: FixtureUser) -> None:
        """Groups correctly by platform and alert."""

        sj1 = test_regular_user.create_scraped_job()
        sj2 = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(platform="linkedin", alert_name="backend", jobs=[sj1])
        test_regular_user.create_job_email(platform="indeed", alert_name="frontend", jobs=[sj2])

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2

        expected_1 = {
            "platform": "linkedin",
            "alert_name": "backend",
            "scraped_count": 1,
            "imported_count": 0,
            "applied_count": 0,
        }
        expected_2 = {
            "platform": "indeed",
            "alert_name": "frontend",
            "scraped_count": 1,
            "imported_count": 0,
            "applied_count": 0,
        }
        assert data[0] == expected_2
        assert data[1] == expected_1

    def test_ignores_other_users_data(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should not include other users' data."""

        test_regular_user.create_job_email(jobs=[test_regular_user.create_scraped_job()])
        test_admin_user.create_job_email(jobs=[test_admin_user.create_scraped_job()])

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1

    def test_no_jobs_returns_empty(self, test_regular_user: FixtureUser) -> None:
        """No scraped jobs should return empty list."""

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthenticated(self, client: TestClient) -> None:
        """Unauthenticated request should return 401."""

        response = client.get(self.endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_scraped_job_in_multiple_alerts_counted_in_each(self, test_regular_user: FixtureUser) -> None:
        """A scraped job linked to two different alerts appears in both groups."""

        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(platform="linkedin", alert_name="backend", jobs=[sj])
        test_regular_user.create_job_email(platform="linkedin", alert_name="python", jobs=[sj])

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2
        by_alert = {row["alert_name"]: row for row in data}
        assert by_alert["backend"]["scraped_count"] == 1
        assert by_alert["python"]["scraped_count"] == 1

    def test_applied_count_uses_application_date(self, test_regular_user: FixtureUser) -> None:
        """A job with only application_date set (no status) still counts as applied."""

        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(jobs=[sj])
        test_regular_user.create_job(scraped_job_id=sj.id, application_date=dt.datetime.now(tz=dt.timezone.utc))

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1

    def test_applied_count_uses_applied_via_and_application_url(self, test_regular_user: FixtureUser) -> None:
        """Jobs with only applied_via or application_url set also count as applied."""

        sj1 = test_regular_user.create_scraped_job()
        sj2 = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(jobs=[sj1, sj2])

        test_regular_user.create_job(scraped_job_id=sj1.id, applied_via="email")
        test_regular_user.create_job(scraped_job_id=sj2.id, application_url="https://example.com/apply")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 2
        assert data[0]["imported_count"] == 2
        assert data[0]["applied_count"] == 2

    def test_applied_count_any_non_applied_status(self, test_regular_user: FixtureUser) -> None:
        """interview, offer, rejected, and withdrawn statuses all count as applied."""

        jobs = []
        for application_status in ("interview", "offer", "rejected", "withdrawn"):
            sj = test_regular_user.create_scraped_job()
            test_regular_user.create_job(scraped_job_id=sj.id, application_status=application_status)
            jobs.append(sj)
        test_regular_user.create_job_email(jobs=jobs)

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 4
        assert data[0]["imported_count"] == 4
        assert data[0]["applied_count"] == 4

    def test_null_alert_name_grouped(self, test_regular_user: FixtureUser) -> None:
        """Emails with no alert_name group correctly (alert_name=None)."""

        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(platform="linkedin", alert_name=None, jobs=[sj])

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["platform"] == "linkedin"
        assert data[0]["alert_name"] is None
        assert data[0]["scraped_count"] == 1

    def test_multiple_jobs_per_scraped_job_no_double_count(self, test_regular_user: FixtureUser) -> None:
        """A scraped job with multiple linked Jobs is counted once in imported and applied."""

        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(jobs=[sj])

        # Two jobs linked to the same scraped job: one plain import, one applied
        test_regular_user.create_job(scraped_job_id=sj.id)
        test_regular_user.create_job(scraped_job_id=sj.id, application_status="applied")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1

    def test_multiple_emails_same_alert_accumulate(self, test_regular_user: FixtureUser) -> None:
        """Multiple emails for the same platform/alert accumulate scraped job counts."""

        test_regular_user.create_job_email(
            platform="indeed", alert_name="data", jobs=[test_regular_user.create_scraped_job()]
        )
        test_regular_user.create_job_email(
            platform="indeed", alert_name="data", jobs=[test_regular_user.create_scraped_job()]
        )

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["platform"] == "indeed"
        assert data[0]["alert_name"] == "data"
        assert data[0]["scraped_count"] == 2

    def test_other_users_imported_job_not_counted(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        """imported_count and applied_count ignore Jobs owned by other users."""

        # Regular user has a scraped job but no linked Job of their own
        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(jobs=[sj])

        # Admin creates a Job pointing at the regular user's scraped job (different owner)
        test_admin_user.create_job(scraped_job_id=sj.id, application_status="applied")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["imported_count"] == 0
        assert data[0]["applied_count"] == 0

    def test_same_scraped_job_in_multiple_emails_not_double_counted(self, test_regular_user: FixtureUser) -> None:
        """A scraped job appearing in two emails of the same alert is counted once, not twice."""

        sj = test_regular_user.create_scraped_job()
        test_regular_user.create_job_email(platform="linkedin", alert_name="backend", jobs=[sj])
        test_regular_user.create_job_email(platform="linkedin", alert_name="backend", jobs=[sj])

        test_regular_user.create_job(scraped_job_id=sj.id, application_status="applied")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1


class TestErrorsOnly:
    """Tests for the errors_only query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    def test_errors_only_false_returns_normal_jobs(self, test_regular_user: FixtureUser) -> None:
        """errors_only=False should return jobs regardless of failure state."""

        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "false"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1

    def test_errors_only_excludes_normal_jobs(self, test_regular_user: FixtureUser) -> None:
        """errors_only=True should return an empty set when no jobs have failed."""

        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0
        assert data["items"] == []

    def test_errors_only_returns_failed_scrape_job(self, test_regular_user: FixtureUser) -> None:
        """A job with a FAILED scrape status must appear when errors_only=True."""

        test_regular_user.create_scraped_job(title="Failed Scrape", status=ProcessingStatus.FAILED)
        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Failed Scrape"

    def test_errors_only_returns_failed_rating_job(self, test_regular_user: FixtureUser) -> None:
        """A job whose JobRating has a FAILED status must appear when errors_only=True."""

        job = test_regular_user.create_scraped_job(title="Failed Rating")
        test_regular_user.create_job_rating(scraped_job=job, status=ProcessingStatus.FAILED)
        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Failed Rating"

    def test_errors_only_returns_both_failure_types(self, test_regular_user: FixtureUser) -> None:
        """Both FAILED scrape jobs and failed-rating jobs appear together."""

        test_regular_user.create_scraped_job(title="Failed Scrape", status=ProcessingStatus.FAILED)
        rating_job = test_regular_user.create_scraped_job(title="Failed Rating")
        test_regular_user.create_job_rating(scraped_job=rating_job, status=ProcessingStatus.FAILED)
        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Failed Scrape", "Failed Rating"}

    def test_errors_only_excludes_successful_rating(self, test_regular_user: FixtureUser) -> None:
        """A job with a successful rating (COMPLETED status) is not returned."""

        job = test_regular_user.create_scraped_job(title="Rated OK")
        test_regular_user.create_job_rating(scraped_job=job, status=ProcessingStatus.COMPLETED)

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_excludes_imported_jobs(self, test_regular_user: FixtureUser) -> None:
        """Imported jobs with a FAILED status must still be excluded by the base filter."""

        test_regular_user.create_scraped_job(title="Imported Failed", status=ProcessingStatus.FAILED, is_imported=True)

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_excludes_inactive_jobs(self, test_regular_user: FixtureUser) -> None:
        """Inactive jobs with a FAILED status must still be excluded by the base filter."""

        test_regular_user.create_scraped_job(title="Inactive Failed", status=ProcessingStatus.FAILED, is_active=False)

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_ignores_deadline_filter(self, test_regular_user: FixtureUser) -> None:
        """errors_only=True should show failed jobs even if their deadline is in the past."""

        past_deadline = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)
        test_regular_user.create_scraped_job(
            title="Past Deadline Failed", status=ProcessingStatus.FAILED, deadline=past_deadline
        )

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1

    def test_errors_only_does_not_return_other_users_jobs(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        """Failed jobs belonging to another user are never returned."""

        test_admin_user.create_scraped_job(title="Admin Failed", status=ProcessingStatus.FAILED)

        response = test_regular_user.client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0


class TestGetExpired:
    """Test suite for GET /scraped-jobs/expired"""

    endpoint = "/scraped-jobs/expired"

    def test_returns_closed_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should return jobs marked as closed."""

        closed = test_regular_user.create_scraped_job(title="Closed Job", is_closed=True)
        test_regular_user.create_scraped_job(title="Active Job", is_closed=False)

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == closed.id

    def test_returns_past_deadline_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should return jobs with a deadline in the past."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)
        future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)
        expired = test_regular_user.create_scraped_job(title="Expired Deadline", deadline=past)
        test_regular_user.create_scraped_job(title="Future Deadline", deadline=future)
        test_regular_user.create_scraped_job(title="No Deadline")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == expired.id

    def test_excludes_imported_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should not return jobs that have already been imported."""

        test_regular_user.create_scraped_job(title="Imported Closed", is_closed=True, is_imported=True)

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_excludes_inactive_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should not return jobs that are already inactive."""

        test_regular_user.create_scraped_job(title="Inactive Closed", is_closed=True, is_active=False)

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_excludes_other_users_jobs(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should not return expired jobs belonging to another user."""

        test_admin_user.create_scraped_job(title="Admin Closed", is_closed=True)

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_returns_empty_when_no_expired_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should return an empty list when there are no expired jobs."""

        test_regular_user.create_scraped_job(title="Normal Job")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthenticated(self, client: TestClient) -> None:
        """Should return 401 when not authenticated."""

        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
