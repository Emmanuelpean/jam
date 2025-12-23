"""Tests for scoring scraped jobs"""

from app.job_rating.scraped_job_rating import score_scraped_jobs
from app.job_email_scraping.models import ScrapedJob
from app import models as app_models
from app.job_rating import models
from app.job_email_scraping.email_parsers import Platform


class TestScoreScrapedJobs(object):

    def test_success(self, session, test_scraped_jobs, test_user_qualifications) -> None:
        """Test scoring scraped jobs successfully"""

        score_scraped_jobs(1, session)
        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 45
        for job_rating in job_ratings:
            assert job_rating.is_success is True
            assert job_rating.overall_score is not None
        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        assert len(service_log.rated_job_found_ids) == 45
        assert len(service_log.rated_job_succeeded_ids) == 45
        assert len(service_log.rated_job_failed_ids) == 0
        assert len(service_log.user_found_ids) == 3
        assert len(service_log.user_processed_ids) == 3

    def test_skipped(self, session, test_scraped_jobs, test_user_qualifications, test_eis_service_logs) -> None:
        """Test scoring scraped jobs successfully"""

        assert (
            session.query(app_models.UserQualification).filter(app_models.UserQualification.owner_id == 3).count() == 0
        )
        # noinspection PyArgumentList
        scraped_job = ScrapedJob(
            external_job_id="skip_this_job",
            platform=Platform.LINKEDIN,
            is_scraped=True,
            is_failed=False,
            description="A valid description.",
            owner_id=3,
            service_log_id=test_eis_service_logs[0].id,
        )
        session.add(scraped_job)
        session.commit()

        score_scraped_jobs(1, session)
        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 45
        for job_rating in job_ratings:
            assert job_rating.is_success is True
            assert job_rating.overall_score is not None
        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        assert len(service_log.rated_job_found_ids) == 45
        assert len(service_log.rated_job_succeeded_ids) == 45
        assert len(service_log.rated_job_failed_ids) == 0
        assert len(service_log.user_found_ids) == 3
        assert len(service_log.user_processed_ids) == 3
