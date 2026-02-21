"""Tests for scoring scraped jobs"""

from app import models
from app.job_email_scraping.email_parsers import Platform
from app.job_rating.scraped_job_rating import score_scraped_jobs


class TestScoreScrapedJobs(object):

    @staticmethod
    def get_premium_users(db) -> list[models.User]:
        """Return premium users list"""
        return db.query(models.User).filter(models.User.premium.has(is_active=True)).all()

    def test_success(self, session, test_scraped_jobs, test_user_qualifications, test_ai_prompts) -> None:
        """Test scoring scraped jobs successfully"""

        score_scraped_jobs(1, session)
        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 34
        for job_rating in job_ratings:
            assert job_rating.is_success is True
            assert job_rating.overall_score is not None
        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        assert len(service_log.job_found_ids) == 34
        assert len(service_log.job_found_ids) == 34
        assert len(service_log.job_failed_ids) == 0
        assert len(service_log.user_found_ids) == len(self.get_premium_users(session))
        assert len(service_log.user_processed_ids) == len(self.get_premium_users(session))
        job_prompt = f"""### Candidate Profile
- **Experience**: Not provided
- **Education**: BSc Computer Science
- **Skills**: Not provided
- **Qualities**: Not provided
- **Interests**: Not provided

### Job Details
- **Title**: {job_ratings[0].scraped_job.title}
- **Company**: {job_ratings[0].scraped_job.company}
- **Description**: {job_ratings[0].scraped_job.description}
"""
        assert job_ratings[0].job_prompt == job_prompt

    def test_skipped(
        self, session, test_scraped_jobs, test_user_qualifications, test_job_scraping_service_logs, test_ai_prompts
    ) -> None:
        """Test scoring scraped jobs successfully"""

        # Add a scraped job for a user without qualifications to test skipping
        assert session.query(models.UserQualification).filter(models.UserQualification.owner_id == 3).count() == 0
        # noinspection PyArgumentList
        scraped_job = models.ScrapedJob(
            external_job_id="skip_this_job",
            platform=Platform.LINKEDIN,
            is_scraped=True,
            is_failed=False,
            description="A valid description.",
            owner_id=3,
            service_log_id=test_job_scraping_service_logs[0].id,
        )
        session.add(scraped_job)
        session.commit()

        score_scraped_jobs(1, session)
        job_ratings = session.query(models.JobRating).all()
        assert len(job_ratings) == 34
        for job_rating in job_ratings:
            assert job_rating.is_success is True
            assert job_rating.overall_score is not None
        service_log = session.query(models.JobRatingServiceLog).first()
        assert service_log is not None
        assert service_log.run_datetime is not None
        assert len(service_log.job_found_ids) == 34
        assert len(service_log.job_succeeded_ids) == 34
        assert len(service_log.job_failed_ids) == 0
        assert len(service_log.user_found_ids) == len(self.get_premium_users(session))
        assert len(service_log.user_processed_ids) == len(self.get_premium_users(session))
