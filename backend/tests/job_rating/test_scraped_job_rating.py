"""Tests for scoring scraped jobs"""

import datetime as dt

from app import models
from app.config import settings
from app.job_email_scraping.email_parsers import Platform
from app.job_rating import scraped_job_rating, schemas
from app.job_rating.prompts import create_system_prompt_with_profile
from app.job_rating.scraped_job_rating import (
    ScrapedJobRatingService,
    ensure_length_limit,
    get_rating_active_users,
    get_user_unrated_scraped_jobs,
)


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

        _, note = ensure_length_limit("title", "x" * 50, 20)
        assert note is not None
        assert note.startswith("Title")


class TestGetRatingActiveUsers:

    def test_returned_users_meet_all_criteria(self, session, test_users) -> None:
        """Test that all returned users are active, verified, and have active job-rating premium."""

        users = get_rating_active_users(session)
        assert len(users) > 0
        for user in users:
            assert user.is_active
            assert user.is_verified
            assert user.premium is not None
            assert user.premium.is_active
            assert user.premium.job_rating_active

    def test_excludes_inactive_users(self, session, test_users) -> None:
        """Test that inactive users are not returned."""

        [inactive_user] = [u for u in test_users if not u.is_active]
        users = get_rating_active_users(session)
        assert inactive_user.id not in [u.id for u in users]

    def test_excludes_unverified_users(self, session, test_users) -> None:
        """Test that unverified users are not returned."""

        [unverified_user] = [u for u in test_users if not u.is_verified]
        users = get_rating_active_users(session)
        assert unverified_user.id not in [u.id for u in users]

    def test_excludes_users_without_active_premium(self, session, test_users) -> None:
        """Test that users without an active premium subscription are not returned."""

        users_without_premium = [u for u in test_users if u.premium is None or not u.premium.is_active]
        assert len(users_without_premium) > 0
        result_ids = [u.id for u in get_rating_active_users(session)]
        for user in users_without_premium:
            assert user.id not in result_ids

    def test_excludes_user_with_job_rating_inactive(self, session, test_users) -> None:
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

    def test_returned_jobs_meet_all_criteria(self, session, test_regular_user, test_scraped_jobs) -> None:
        """Test that all returned jobs are eligible for rating."""

        jobs = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert len(jobs) > 0
        for job in jobs:
            assert job.owner_id == test_regular_user.id
            assert job.job_rating is None
            assert job.is_processed is True
            assert job.is_scraped is True
            assert job.is_failed is False
            assert job.is_active is True
            assert job.is_imported is False
            assert job.exclusion_filter is None

    def test_excludes_jobs_of_other_users(self, session, test_regular_user, test_scraped_jobs) -> None:
        """Test that only jobs belonging to the given user are returned."""

        jobs = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        for job in jobs:
            assert job.owner_id == test_regular_user.id

    def test_excludes_already_rated_job(
        self, session, test_regular_user, test_scraped_jobs, test_user_qualifications, test_ai_prompts
    ) -> None:
        """Test that already rated jobs are excluded."""

        jobs_before = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert len(jobs_before) > 0
        job = jobs_before[0]

        qualification = [q for q in test_user_qualifications if q.owner_id == test_regular_user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        session.add(
            models.JobRating(
                scraped_job_id=job.id,
                owner_id=test_regular_user.id,
                user_qualification_id=qualification.id,
                system_prompt_id=system_prompt.id,
                job_prompt_template_id=job_prompt_template.id,
                is_success=True,
                llm_model="chatgpt",
            )
        )
        session.commit()

        jobs_after = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert job.id not in [j.id for j in jobs_after]
        assert len(jobs_after) == len(jobs_before) - 1

    def test_excludes_inactive_job(self, session, test_regular_user, test_scraped_jobs) -> None:
        """Test that inactive jobs are excluded."""

        jobs_before = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        job = jobs_before[0]
        job.is_active = False
        session.commit()

        jobs_after = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert job.id not in [j.id for j in jobs_after]
        assert len(jobs_after) == len(jobs_before) - 1

    def test_excludes_failed_job(self, session, test_regular_user, test_scraped_jobs) -> None:
        """Test that failed jobs are excluded."""

        jobs_before = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        job = jobs_before[0]
        job.is_failed = True
        session.commit()

        jobs_after = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert job.id not in [j.id for j in jobs_after]
        assert len(jobs_after) == len(jobs_before) - 1

    def test_excludes_imported_job(self, session, test_regular_user, test_scraped_jobs) -> None:
        """Test that imported jobs are excluded."""

        jobs_before = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        job = jobs_before[0]
        job.is_imported = True
        session.commit()

        jobs_after = get_user_unrated_scraped_jobs(session, test_regular_user.id)
        assert job.id not in [j.id for j in jobs_after]
        assert len(jobs_after) == len(jobs_before) - 1


class TestScrapedJobRaterRateJob:

    @staticmethod
    def make_service_log(session) -> models.JobRatingServiceLog:
        """Create a service log for testing"""
        service_log = models.JobRatingServiceLog(run_datetime=dt.datetime.now())
        session.add(service_log)
        session.commit()
        session.refresh(service_log)
        return service_log

    @staticmethod
    def make_scraped_job(session, user_id, description, service_log_id) -> models.ScrapedJob:
        """Create a scraped job with the given description.
        :param session: database session
        :param user_id: user ID of the scraped job owner
        :param description: job description
        :param service_log_id: service log ID to associate with the scraped job
        :return: the created scraped job"""

        scraped_job = models.ScrapedJob(
            external_job_id=f"test_{dt.datetime.now().timestamp()}",
            platform=Platform.LINKEDIN,
            is_scraped=True,
            is_processed=True,
            is_failed=False,
            title="Test Job Title",
            company="Test Company",
            description=description,
            owner_id=user_id,
            service_log_id=service_log_id,
        )
        session.add(scraped_job)
        session.commit()
        session.refresh(scraped_job)
        return scraped_job

    def test_skips_job_with_short_description(
        self,
        session,
        test_users,
        test_user_qualifications,
        test_ai_prompts,
        test_job_scraping_service_logs,
    ) -> None:
        """Test that a job whose description is too short is marked as skipped."""

        user = test_users[0]
        qualification = [q for q in test_user_qualifications if q.owner_id == user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.make_service_log(session)
        scraped_job = self.make_scraped_job(session, user.id, "Short", test_job_scraping_service_logs[0].id)

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

        session.refresh(service_log)
        rating = session.query(models.JobRating).filter(models.JobRating.scraped_job_id == scraped_job.id).first()
        assert rating is not None
        assert rating.is_skipped is True
        assert "Job description too short" in rating.skip_reason
        assert scraped_job.id in service_log.job_skipped_ids

    def test_successful_rating(
        self,
        session,
        test_users,
        test_user_qualifications,
        test_ai_prompts,
        test_job_scraping_service_logs,
    ) -> None:
        """Test that a job with a valid description is rated and saved successfully."""

        user = test_users[0]
        qualification = [q for q in test_user_qualifications if q.owner_id == user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.make_service_log(session)
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(session, user.id, description, test_job_scraping_service_logs[0].id)

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

        session.refresh(service_log)
        rating = session.query(models.JobRating).filter(models.JobRating.scraped_job_id == scraped_job.id).first()
        assert rating is not None
        assert rating.is_success is True
        assert rating.overall_score is not None
        assert rating.job_prompt is not None
        assert scraped_job.id in service_log.job_succeeded_ids

    def test_failed_rating(
        self,
        session,
        test_users,
        test_user_qualifications,
        test_ai_prompts,
        test_job_scraping_service_logs,
        monkeypatch,
    ) -> None:
        """Test that an AI scoring error creates a failed job rating entry."""

        user = test_users[0]
        qualification = [q for q in test_user_qualifications if q.owner_id == user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.make_service_log(session)
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(session, user.id, description, test_job_scraping_service_logs[0].id)

        import app.job_rating.scraped_job_rating as rating_module

        def raise_error(*_args, **_kwargs):
            """Raise an error"""
            raise RuntimeError("AI service unavailable")

        monkeypatch.setattr(rating_module, "claude_query", raise_error)

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

        session.refresh(service_log)

        # First failure leaves a pending JobRating (is_success None) with a retry scheduled
        rating = session.query(models.JobRating).filter(models.JobRating.scraped_job_id == scraped_job.id).first()
        assert rating is not None
        assert rating.is_success is None
        assert rating.rating_retry_count == 1
        assert rating.rating_next_retry_at is not None
        assert scraped_job.id in service_log.job_failed_ids

        # The failure is recorded as a unified Error
        service_error = session.query(models.ServiceError).first()
        assert service_error is not None
        assert "AI service unavailable" in service_error.message
        # The rating error is linked to the pending JobRating and the rating run (not the ScrapedJob)
        assert service_error.scraped_job_id is None
        assert service_error.job_rating_id == rating.id
        assert service_error.job_rating_service_log_id == service_log.id
        # Per-job rating errors fall to the default (non-critical) level
        assert service_error.level == "error"

    def test_rating_permanently_fails_after_max_retries(
        self,
        session,
        test_users,
        test_user_qualifications,
        test_ai_prompts,
        test_job_scraping_service_logs,
        monkeypatch,
    ) -> None:
        """After settings.rating_max_retry failures a terminal failed JobRating is created."""

        user = test_users[0]
        qualification = [q for q in test_user_qualifications if q.owner_id == user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.make_service_log(session)
        description = "A" * (settings.min_scraping_description_length + 1)
        scraped_job = self.make_scraped_job(session, user.id, description, test_job_scraping_service_logs[0].id)

        import app.job_rating.scraped_job_rating as rating_module

        def raise_error(*_args, **_kwargs):
            """Raise an error"""
            raise RuntimeError("AI service unavailable")

        monkeypatch.setattr(rating_module, "claude_query", raise_error)

        combined_system_prompt = create_system_prompt_with_profile(
            system_prompt.prompt,
            qualification.experience,
            qualification.education,
            qualification.skills,
            qualification.qualities,
            qualification.interests,
        )

        rater = ScrapedJobRatingService()
        for _ in range(settings.rating_max_retry):
            rater._rate_job(
                session,
                scraped_job,
                user.id,
                qualification,
                service_log,
                system_prompt,
                job_prompt_template,
                combined_system_prompt,
            )
            # Clear the scheduled retry so the next iteration re-attempts immediately
            rating = session.query(models.JobRating).filter_by(scraped_job_id=scraped_job.id).first()
            rating.rating_next_retry_at = None
            session.commit()

        session.refresh(scraped_job)

        # The rating fails permanently (is_success False) so the job is no longer re-queried
        rating = session.query(models.JobRating).filter(models.JobRating.scraped_job_id == scraped_job.id).first()
        assert rating is not None
        assert rating.is_success is False
        assert rating.rating_retry_count == settings.rating_max_retry

        # Every attempt is recorded as an Error
        assert session.query(models.ServiceError).count() == settings.rating_max_retry

        # Rating errors surface on JobRating.rating_errors, not on ScrapedJob.scraping_errors
        session.refresh(rating)
        assert len(rating.rating_errors) == settings.rating_max_retry
        assert all(e.job_rating_id == rating.id for e in rating.rating_errors)
        assert all(e.job_rating_service_log_id is not None for e in rating.rating_errors)
        assert all(e.level == "error" for e in rating.rating_errors)
        assert scraped_job.scraping_errors == []

    def test_truncates_long_description(
        self,
        session,
        test_users,
        test_user_qualifications,
        test_ai_prompts,
        test_job_scraping_service_logs,
    ) -> None:
        """Test that a description exceeding the max length is truncated and a note is recorded."""

        user = test_users[0]
        qualification = [q for q in test_user_qualifications if q.owner_id == user.id][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.make_service_log(session)
        description = "A" * (settings.max_scraping_description_length + 100)
        scraped_job = self.make_scraped_job(session, user.id, description, test_job_scraping_service_logs[0].id)

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

        rating = session.query(models.JobRating).filter(models.JobRating.scraped_job_id == scraped_job.id).first()
        assert rating is not None
        assert rating.is_success is True
        assert rating.notes is not None and len(rating.notes) > 0
        assert any("description" in note.lower() for note in rating.notes)


class TestScrapedJobRaterProcessUser:

    @staticmethod
    def create_service_log(session) -> models.JobRatingServiceLog:
        """Create a service log for testing"""

        service_log = models.JobRatingServiceLog(run_datetime=dt.datetime.now())
        session.add(service_log)
        session.commit()
        session.refresh(service_log)
        return service_log

    def test_skips_user_without_qualification(
        self, session, test_users, test_scraped_jobs, test_user_qualifications, test_ai_prompts
    ) -> None:
        """Test that a user with no qualification is skipped and not added to user_processed_ids."""

        user = [u for u in test_users if not any(q.owner_id == u.id for q in test_user_qualifications)][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.create_service_log(session)

        ScrapedJobRatingService()._process_user(session, user.id, service_log, system_prompt, job_prompt_template)

        session.refresh(service_log)
        assert user.id not in service_log.user_processed_ids

    def test_adds_user_to_processed_ids(
        self, session, test_users, test_scraped_jobs, test_user_qualifications, test_ai_prompts
    ) -> None:
        """Test that a successfully processed user is added to user_processed_ids."""

        user = [u for u in test_users if any(q.owner_id == u.id for q in test_user_qualifications)][0]
        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.create_service_log(session)

        ScrapedJobRatingService()._process_user(session, user.id, service_log, system_prompt, job_prompt_template)

        session.refresh(service_log)
        assert user.id in service_log.user_processed_ids

    def test_adds_jobs_to_found_ids(
        self, session, test_users, test_scraped_jobs, test_user_qualifications, test_ai_prompts
    ) -> None:
        """Test that found jobs for the user are recorded in job_found_ids."""

        user = test_users[0]
        expected_jobs = get_user_unrated_scraped_jobs(session, user.id)
        assert len(expected_jobs) > 0

        system_prompt, job_prompt_template = test_ai_prompts
        service_log = self.create_service_log(session)

        ScrapedJobRatingService()._process_user(session, user.id, service_log, system_prompt, job_prompt_template)

        session.refresh(service_log)
        for job in expected_jobs:
            assert job.id in service_log.job_found_ids


class TestScoreScrapedJobs(object):

    @staticmethod
    def get_premium_users(db) -> list[models.User]:
        """Return premium users list"""
        return db.query(models.User).filter(models.User.premium.has(is_active=True)).all()

    def test_success(self, session, test_scraped_jobs, test_user_qualifications, test_ai_prompts, monkeypatch) -> None:
        """Test scoring scraped jobs successfully"""

        monkeypatch.setattr(settings, "min_scraping_description_length", 70)
        ScrapedJobRatingService().run(session)
        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 34
        for job_rating in job_ratings:
            assert job_rating.is_success is True or job_rating.is_skipped is True
        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        assert len(service_log.job_found_ids) == 34
        assert len(service_log.job_succeeded_ids) == 13
        assert len(service_log.job_skipped_ids) == 21
        assert len(service_log.job_failed_ids) == 0
        assert len(service_log.user_found_ids) == 3
        assert len(service_log.user_processed_ids) == 3

        # Check that the job prompt contains only job details (candidate profile is in system prompt)
        job_rating = [job_rating for job_rating in job_ratings if job_rating.is_success][0]
        job_prompt = f"""### Job Details
- **Title**: {job_rating.scraped_job.title}
- **Company**: {job_rating.scraped_job.company}
- **Description**: {job_rating.scraped_job.description}
"""
        assert job_prompt in job_rating.job_prompt

        # Check that the is_closed jobs are skipped
        scraped_job = [scraped_job for scraped_job in test_scraped_jobs if scraped_job.is_closed][0]
        job_rating = [job_rating for job_rating in job_ratings if job_rating.scraped_job.id == scraped_job.id][0]
        assert job_rating.is_skipped is True
        assert "is closed" in job_rating.skip_reason.lower()

        # Check that past deadline jobs are skipped
        scraped_job = [
            scraped_job
            for scraped_job in test_scraped_jobs
            if scraped_job.deadline and scraped_job.deadline < dt.datetime.now(dt.timezone.utc)
        ][0]
        job_rating = [job_rating for job_rating in job_ratings if job_rating.scraped_job.id == scraped_job.id][0]
        assert job_rating.is_skipped is True
        assert "is closed" in job_rating.skip_reason.lower()

        # Check that upcoming deadline jobs are not skipped
        scraped_job = [
            scraped_job
            for scraped_job in test_scraped_jobs
            if scraped_job.deadline and scraped_job.deadline > dt.datetime.now(dt.timezone.utc)
        ][0]
        job_rating = [job_rating for job_rating in job_ratings if job_rating.scraped_job.id == scraped_job.id][0]
        assert job_rating.is_skipped is False

    def test_critical_error_is_recorded_as_error(
        self, session, test_scraped_jobs, test_user_qualifications, test_ai_prompts, monkeypatch
    ) -> None:
        """Test that an unexpected error in the rating workflow is recorded as a unified Error."""

        def raise_error(_):
            raise RuntimeError("DB connection lost")

        monkeypatch.setattr(scraped_job_rating, "get_rating_active_users", raise_error)

        service_log = ScrapedJobRatingService().run(session)

        assert schemas.JobRatingServiceLogOut.model_validate(service_log, from_attributes=True).is_success is False
        error = session.query(models.ServiceError).filter_by(job_rating_service_log_id=service_log.id).one()
        assert "DB connection lost" in error.message
        assert error.scraped_job_id is None
        assert error.level == "critical"
