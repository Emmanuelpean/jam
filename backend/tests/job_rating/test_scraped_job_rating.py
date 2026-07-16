"""Tests for scoring scraped jobs"""

import datetime as dt
from contextlib import nullcontext
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app import models
from app.base_models import ProcessingStatus
from app.config import settings
from app.job_rating import scraped_job_rating
from app.job_rating.prompts import Prompts, create_system_prompt_with_profile
from app.job_rating.scraped_job_rating import (
    ScrapedJobRatingService,
    ensure_length_limit,
    get_rating_active_users,
    get_user_unrated_scraped_jobs,
)
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


class TestEnsureLengthLimit:

    def test_within_limit(self) -> None:
        """Test that text within the limit is returned unchanged."""

        text = "Short text"
        result_text, note = ensure_length_limit("description", text, 100)
        assert result_text == text
        assert note is None

    def test_at_limit(self) -> None:
        """Test that text at the exact limit is returned unchanged."""

        text = "x" * 100
        result_text, note = ensure_length_limit("description", text, 100)
        assert result_text == text
        assert note is None

    def test_exceeds_limit(self) -> None:
        """Test that text exceeding the limit is truncated and a note is returned."""

        text = "x" * 200
        max_length = 100
        result_text, note = ensure_length_limit("description", text, max_length)
        assert result_text == "x" * max_length + "..."
        truncated_len = max_length + len("...")
        assert (
            note
            == f"Description was truncated as it was too long ({truncated_len} characters. Limit is {max_length} characters)"
        )

    def test_text_describer_is_capitalised_in_note(self) -> None:
        """Test that the text describer is capitalised in the truncation note."""

        note = ensure_length_limit("title", "x" * 50, 20)[1]
        assert note is not None
        assert note.startswith("Title")


class TestGetRatingActiveUsers:

    def test_returned_users_meet_all_criteria(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Test that all returned users are active, verified, and have active job-rating premium."""

        users = get_rating_active_users(session)
        assert len(users) > 0
        for user in users:
            assert user.is_active
            assert user.is_verified
            assert user.premium is not None
            assert user.premium.is_active
            assert user.premium.job_rating_active

    def test_excludes_inactive_users(
        self, session: Session, test_regular_user: FixtureUser, test_inactive_user: FixtureUser
    ) -> None:
        """Test that inactive users are not returned."""

        users = get_rating_active_users(session)
        assert test_inactive_user.id not in [u.id for u in users]

    def test_excludes_unverified_users(
        self, session: Session, test_regular_user: FixtureUser, test_unverified_user: FixtureUser
    ) -> None:
        """Test that unverified users are not returned."""

        users = get_rating_active_users(session)
        assert test_unverified_user.id not in [u.id for u in users]

    def test_excludes_users_without_active_premium(
        self, session: Session, test_regular_user: FixtureUser, test_non_premium_user: FixtureUser
    ) -> None:
        """Test that users without an active premium subscription are not returned."""

        result_ids = [u.id for u in get_rating_active_users(session)]
        assert test_non_premium_user.id not in result_ids

    def test_excludes_user_with_job_rating_inactive(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Test that users with job_rating_active=False are not returned."""

        eligible_users = get_rating_active_users(session)
        assert len(eligible_users) > 0

        # Disable job rating for one user and verify they are excluded
        user = eligible_users[0]
        user.premium.job_rating_active = False
        session.commit()

        updated_users = get_rating_active_users(session)
        assert user.id not in [u.id for u in updated_users]


class TestGetUserUnratedScrapedJobs:

    @staticmethod
    @pytest.fixture
    def scraped_jobs(test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> dict[str, models.ScrapedJob]:
        """One scraped job of every category `get_user_unrated_scraped_jobs` discriminates on.

        Two are rating-eligible (`eligible`, `pending_rating`); the rest are each excluded for a
        single reason, so a test can assert exactly which jobs the query returns."""

        exclusion_filter = test_regular_user.create_scraping_exclusion_filter()

        jobs = {
            # Eligible: completed and either unrated or with a still-pending rating.
            "eligible": test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED),
            "pending_rating": test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED),
            # Excluded, one reason each.
            "finalised_rating": test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED),
            "not_processed": test_regular_user.create_scraped_job(status=ProcessingStatus.PENDING),
            "not_scraped": test_regular_user.create_scraped_job(status=ProcessingStatus.FILTERED),
            "failed": test_regular_user.create_scraped_job(status=ProcessingStatus.FAILED),
            "inactive": test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED, is_active=False),
            "imported": test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED, is_imported=True),
            "filtered": test_regular_user.create_scraped_job(
                status=ProcessingStatus.COMPLETED, exclusion_filter_id=exclusion_filter.id
            ),
            "other_user": test_admin_user.create_scraped_job(status=ProcessingStatus.COMPLETED),
        }

        # A pending rating keeps the job eligible; a finalised (succeeded) one does not.
        test_regular_user.create_job_rating(scraped_job=jobs["pending_rating"])
        test_regular_user.create_job_rating(scraped_job=jobs["finalised_rating"], status=ProcessingStatus.COMPLETED)

        return jobs

    def test_returns_only_eligible_jobs(
        self, session: Session, test_regular_user: FixtureUser, scraped_jobs: dict[str, models.ScrapedJob]
    ) -> None:
        """Test that exactly the eligible (unrated or pending-rating) jobs are returned."""

        returned_ids = {job.id for job in get_user_unrated_scraped_jobs(session, test_regular_user.id)}
        assert returned_ids == {scraped_jobs["eligible"].id, scraped_jobs["pending_rating"].id}

    def test_returned_jobs_meet_all_criteria(
        self, session: Session, test_regular_user: FixtureUser, scraped_jobs: dict[str, models.ScrapedJob]
    ) -> None:
        """Test that all returned jobs satisfy every eligibility criterion."""

        jobs = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert len(jobs) > 0
        for job in jobs:
            assert job.owner_id == test_regular_user.id
            assert job.status == ProcessingStatus.COMPLETED
            assert job.is_active is True
            assert job.is_imported is False
            assert job.exclusion_filter is None
            assert job.job_rating is None or job.job_rating.is_pending

    @pytest.mark.parametrize(
        "category",
        [
            "finalised_rating",
            "not_processed",
            "not_scraped",
            "failed",
            "inactive",
            "imported",
            "filtered",
            "other_user",
        ],
    )
    def test_excludes_ineligible_jobs(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        scraped_jobs: dict[str, models.ScrapedJob],
        category: str,
    ) -> None:
        """Test that each kind of ineligible job is excluded from the results."""

        returned_ids = [job.id for job in get_user_unrated_scraped_jobs(session, test_regular_user.id)]
        assert scraped_jobs[category].id not in returned_ids


class TestScrapedJobRaterRateJob(BaseTest):

    @staticmethod
    def make_scraped_job(user: FixtureUser, description: str) -> models.ScrapedJob:
        """Create a scraped, processed job with the given description, ready to be rated."""
        return user.create_scraped_job(
            status=ProcessingStatus.COMPLETED,
            title="Test Job Title",
            company="Test Company",
            description=description,
        )

    @staticmethod
    def rate_job(
        session: Session,
        scraped_job: models.ScrapedJob,
        user: FixtureUser,
        qualification: models.UserQualification,
        service_log: models.JobRatingServiceLog,
        prompts: Prompts,
    ) -> None:
        """Rate a scraped job, building the combined system prompt from the user's qualification."""

        system_prompt, job_prompt_template = prompts
        combined_system_prompt = create_system_prompt_with_profile(
            system_prompt.prompt,
            qualification.experience,
            qualification.education,
            qualification.skills,
            qualification.qualities,
            qualification.interests,
        )
        ScrapedJobRatingService()._rate_job(
            session,
            scraped_job,
            user.id,
            qualification,
            service_log,
            system_prompt,
            job_prompt_template,
            combined_system_prompt,
        )

    @staticmethod
    def get_rating(session: Session, scraped_job: models.ScrapedJob) -> models.JobRating | None:
        """Return the job rating for the given scraped job, if any."""
        return session.query(models.JobRating).filter_by(scraped_job_id=scraped_job.id).first()

    def test_skips_job_with_short_description(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that a job whose description is too short is marked as skipped."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        scraped_job = self.make_scraped_job(test_regular_user, "Short")

        self.rate_job(session, scraped_job, test_regular_user, qualification, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)
        rating = self.get_rating(session, scraped_job)
        assert rating is not None
        assert rating.status == ProcessingStatus.SKIPPED
        assert "Job description too short" in rating.skip_reason
        assert scraped_job.id in test_rating_service_log.job_skipped_ids

    def test_successful_rating(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that a job with a valid description is rated and saved successfully."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(test_regular_user, description)

        self.rate_job(session, scraped_job, test_regular_user, qualification, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)
        rating = self.get_rating(session, scraped_job)
        assert rating is not None
        assert rating.status == ProcessingStatus.COMPLETED
        assert rating.overall_score is not None
        assert rating.job_prompt is not None
        assert rating.service_log_id == test_rating_service_log.id
        assert scraped_job.id in test_rating_service_log.job_succeeded_ids

    def test_failed_rating(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        monkeypatch: pytest.MonkeyPatch,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that an AI scoring error creates a failed job rating entry."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(test_regular_user, description)

        def raise_error(*_args, **_kwargs):
            """Raise an error"""
            raise RuntimeError("AI service unavailable")

        monkeypatch.setattr(scraped_job_rating, "claude_query", raise_error)

        self.rate_job(session, scraped_job, test_regular_user, qualification, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)

        # First failure leaves a PENDING JobRating with a retry scheduled
        rating = self.get_rating(session, scraped_job)
        assert rating is not None
        assert rating.status == ProcessingStatus.PENDING
        assert rating.rating_retry_count == 1
        assert rating.rating_next_retry_at is not None
        assert scraped_job.id in test_rating_service_log.job_failed_ids
        assert len(rating.rating_errors) == 1
        service_error = rating.rating_errors[0]
        # Static message; the exception text and job id are carried in context.
        assert service_error.message == "Error scoring job."
        assert service_error.context["job_id"] == scraped_job.id
        assert "AI service unavailable" in service_error.context["error"]
        assert service_error.scraped_job_id is None
        assert service_error.job_rating_id == rating.id
        assert service_error.job_rating_service_log_id == test_rating_service_log.id
        assert service_error.level == "error"

    def test_rating_permanently_fails_after_max_retries(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        monkeypatch: pytest.MonkeyPatch,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """After settings.rating_max_retry failures a terminal failed JobRating is created."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(test_regular_user, description)

        def raise_error(*_args, **_kwargs):
            """Raise an error"""
            raise RuntimeError("AI service unavailable")

        monkeypatch.setattr(scraped_job_rating, "claude_query", raise_error)

        for _ in range(settings.rating_max_retry):
            self.rate_job(
                session, scraped_job, test_regular_user, qualification, test_rating_service_log, test_ai_prompts
            )
            # Clear the scheduled retry so the next iteration re-attempts immediately
            rating = self.get_rating(session, scraped_job)
            rating.rating_next_retry_at = None
            session.commit()

        session.refresh(scraped_job)

        # The rating fails permanently (status FAILED) so the job is no longer re-queried
        rating = self.get_rating(session, scraped_job)
        assert rating is not None
        assert rating.status == ProcessingStatus.FAILED
        assert rating.rating_retry_count == settings.rating_max_retry
        assert len(rating.rating_errors) == settings.rating_max_retry
        assert all(e.job_rating_id == rating.id for e in rating.rating_errors)
        assert all(e.job_rating_service_log_id is not None for e in rating.rating_errors)
        assert all(e.level == "error" for e in rating.rating_errors)

    def test_truncates_long_description(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that a description exceeding the max length is truncated and a note is recorded."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        description = "A" * (settings.max_scraping_description_length + 100)
        scraped_job = self.make_scraped_job(test_regular_user, description)

        self.rate_job(session, scraped_job, test_regular_user, qualification, test_rating_service_log, test_ai_prompts)

        rating = self.get_rating(session, scraped_job)
        assert rating is not None
        assert rating.status == ProcessingStatus.COMPLETED
        assert rating.notes is not None and len(rating.notes) > 0
        assert any("description" in note.lower() for note in rating.notes)


class TestScrapedJobRaterProcessUser(BaseTest):

    @staticmethod
    def process_user(
        session: Session,
        user: FixtureUser,
        service_log: models.JobRatingServiceLog,
        prompts: Prompts,
    ) -> None:
        """Process a single user's unrated scraped jobs."""
        system_prompt, job_prompt_template = prompts
        ScrapedJobRatingService()._process_user(session, user.id, service_log, system_prompt, job_prompt_template)

    def test_skips_user_without_qualification(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that a user with no qualification is skipped and not added to user_processed_ids."""

        self.process_user(session, test_regular_user, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)
        assert test_regular_user.id not in test_rating_service_log.user_processed_ids

    def test_adds_user_to_processed_ids(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that a successfully processed user is added to user_processed_ids."""

        test_regular_user.create_user_qualification(experience="QA")

        self.process_user(session, test_regular_user, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)
        assert test_regular_user.id in test_rating_service_log.user_processed_ids

    def test_adds_jobs_to_found_ids(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        test_rating_service_log: models.JobRatingServiceLog,
    ) -> None:
        """Test that found jobs for the user are recorded in job_found_ids."""

        test_regular_user.create_user_qualification(experience="QA")
        test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED)
        test_regular_user.create_scraped_job(status=ProcessingStatus.COMPLETED)
        expected_jobs = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert len(expected_jobs) > 0

        self.process_user(session, test_regular_user, test_rating_service_log, test_ai_prompts)

        session.refresh(test_rating_service_log)
        for job in expected_jobs:
            assert job.id in test_rating_service_log.job_found_ids


class TestScoreScrapedJobs(BaseTest):

    @pytest.fixture(autouse=True)
    def _run_within_test_session(self, session: Session):
        """Make ScrapedJobRatingService.run()'s own db_session() reuse the test's transactional session."""

        with patch.object(scraped_job_rating, "db_session", side_effect=lambda: nullcontext(session)):
            yield

    @staticmethod
    def create_rateable_job(user: FixtureUser, **kwargs) -> models.ScrapedJob:
        """Create a scraped, processed job eligible for rating, overriding fields via kwargs."""
        data = {
            "status": ProcessingStatus.COMPLETED,
            "title": "Test Job Title",
            "company": "Test Company",
            "description": "A" * 100,
            **kwargs,
        }
        return user.create_scraped_job(**data)

    def test_success(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_ai_prompts: Prompts,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test scoring scraped jobs successfully, with one job per rating outcome."""

        monkeypatch.setattr(settings, "min_scraping_description_length", 70)
        test_regular_user.create_user_qualification(experience="10 years Python", education="BSc Computer Science")

        now = dt.datetime.now(dt.timezone.utc)
        succeeded_job = self.create_rateable_job(test_regular_user)
        upcoming_job = self.create_rateable_job(test_regular_user, deadline=now + dt.timedelta(days=30))
        closed_job = self.create_rateable_job(test_regular_user, is_closed=True)
        past_deadline_job = self.create_rateable_job(test_regular_user, deadline=now - dt.timedelta(days=1))
        short_job = self.create_rateable_job(test_regular_user, description="Too short")
        no_description_job = self.create_rateable_job(test_regular_user, description=None)

        ScrapedJobRatingService().run()

        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 6
        for job_rating in job_ratings:
            assert job_rating.status == ProcessingStatus.COMPLETED or job_rating.status == ProcessingStatus.SKIPPED
        ratings_by_job = {job_rating.scraped_job_id: job_rating for job_rating in job_ratings}

        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        all_jobs = (succeeded_job, upcoming_job, closed_job, past_deadline_job, short_job, no_description_job)
        assert set(service_log.job_found_ids) == {job.id for job in all_jobs}
        assert set(service_log.job_succeeded_ids) == {succeeded_job.id, upcoming_job.id}
        assert set(service_log.job_skipped_ids) == {
            closed_job.id,
            past_deadline_job.id,
            short_job.id,
            no_description_job.id,
        }
        assert service_log.job_failed_ids == []
        assert service_log.user_found_ids == [test_regular_user.id]
        assert service_log.user_processed_ids == [test_regular_user.id]

        # Check that the job prompt contains only job details (candidate profile is in system prompt)
        succeeded_rating = ratings_by_job[succeeded_job.id]
        job_prompt = f"""### Job Details
- **Title**: {succeeded_job.title}
- **Company**: {succeeded_job.company}
- **Description**: {succeeded_job.description}
"""
        assert job_prompt in succeeded_rating.job_prompt

        # A closed job and a job past its deadline are both skipped as closed
        for job in (closed_job, past_deadline_job):
            assert ratings_by_job[job.id].status == ProcessingStatus.SKIPPED
            assert "is closed" in ratings_by_job[job.id].skip_reason.lower()

        # A job with an upcoming deadline is not skipped
        assert ratings_by_job[upcoming_job.id].status == ProcessingStatus.COMPLETED

    def test_critical_error_is_recorded_as_error(self, session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that an unexpected error in the rating workflow is recorded as a unified Error."""

        def raise_error(_):
            """Raise an error"""
            raise RuntimeError("DB connection lost")

        monkeypatch.setattr(scraped_job_rating, "get_rating_active_users", raise_error)

        service_log = ScrapedJobRatingService().run()
        error = service_log.service_errors[0]
        assert error.error_type == "RuntimeError"
        assert "DB connection lost" in error.traceback
        assert error.scraped_job_id is None
        assert error.level == "critical"
