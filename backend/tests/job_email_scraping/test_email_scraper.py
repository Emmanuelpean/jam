"""Test module for email_scaper.py functions and JobScraper class"""

import datetime as dt
from functools import partial
from typing import Callable
from unittest import mock
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.emails.schemas import EmailData
from app.job_email_scraping.email_parsers.utils import Platform, remove_style_tags
from app.job_email_scraping.email_scraper import JobEmailScrapingService
from app.job_email_scraping.schemas import JobResult
from app.base_models import ProcessingStatus
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser
from tests.job_email_scraping.mock_job_scrapers import MockIndeedBrightdataJobScraper
from tests.utils import job_email_resources as resources

# ---------------------------------------------------- EMAIL METHODS ---------------------------------------------------


class TestSaveEmailToDb(BaseTest):
    """Test class for JobScraper.save_email_to_db method"""

    def test_save_new_email_success(self, test_regular_user: FixtureUser, session: Session) -> None:
        """Test saving a new email successfully"""

        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        for email_id in resources.TEST_EMAILS:
            result_email, is_created = service.get_and_save_email_to_db(
                session, email_id, test_regular_user, service_log.id
            )

            assert is_created
            assert result_email
            assert result_email.external_email_id == email_id
            assert result_email.subject
            assert result_email.sender == resources.TEST_EMAILS[email_id]["to"]
            assert result_email.platform == resources.TEST_EMAILS[email_id]["platform"]
            assert result_email.body == remove_style_tags(resources.TEST_EMAILS[email_id]["body"])
            assert result_email.owner_id
            assert result_email.alert_name == resources.TEST_EMAILS[email_id]["alert_name"]
            assert result_email.service_log_id == service_log.id

    def test_save_existing_email_returns_existing(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser, session: Session
    ) -> None:
        """Test that existing email is returned without creating a new record"""
        service = JobEmailScrapingService()

        message_id = list(resources.TEST_EMAILS.keys())[0]

        existing_email = test_regular_user.create_job_email(
            external_email_id=message_id,
            subject="Different Subject",
            sender="different@example.com",
            platform="indeed",
            body="Different body content",
        )

        # Try to save it with a different user
        result_email, is_created = service.get_and_save_email_to_db(
            session, message_id, test_admin_user, existing_email.service_log_id
        )

        assert is_created is False
        assert result_email
        assert result_email.id == existing_email.id
        assert result_email.subject == "Different Subject"

        # Verify only one record exists
        email_count = session.query(models.JobEmail).count()
        assert email_count == 1


# ----------------------------------------------------- JOB METHODS ----------------------------------------------------


class TestSaveJobBaseInfoToDb:
    """Test class for JobScraper.save_job_base_info_to_db method"""

    def test_save_new_jobs_success(
        self,
        test_regular_user: FixtureUser,
        session: Session,
    ) -> None:
        """Test saving new job IDs successfully"""

        service = JobEmailScrapingService()
        email = test_regular_user.create_job_email()
        jobs = resources.LINKEDIN_EMAIL_4_EXTRACTED
        result = service.save_job_base_info_to_db(session, email_record=email, job_results=jobs)

        # Verify returned list has correct length
        assert len(result) == len(jobs)

        # Verify all jobs are owned by the email's owner and linked back to it
        for job_record in result:
            assert job_record.owner_id == test_regular_user.id
            assert job_record.external_job_id in [job.job_id for job in jobs]
            assert email in job_record.emails

    def test_save_existing_jobs_returns_existing(
        self,
        test_regular_user: FixtureUser,
        session: Session,
    ) -> None:
        """Test that existing jobs are returned without creating duplicates"""
        service = JobEmailScrapingService()

        email_data = resources.LINKEDIN_EMAIL_4
        jobs = email_data["parsed_output"]

        email = test_regular_user.create_job_email()
        # Pre-create the scraped job for the first result so it must be reused, not duplicated
        test_regular_user.create_scraped_job(external_job_id=jobs[0].job_id, platform=email_data["platform"])

        result = service.save_job_base_info_to_db(session, email_record=email, job_results=jobs)

        assert len(result) == len(jobs)
        # No duplicate created for the already-existing job
        assert session.query(models.ScrapedJob).count() == len(jobs)

    def test_save_jobs_different_owners(
        self,
        test_regular_user: FixtureUser,
        test_admin_user: FixtureUser,
        session: Session,
    ) -> None:
        """Test that jobs with same external_job_id but different owners are created separately"""
        service = JobEmailScrapingService()

        jobs = resources.LINKEDIN_EMAIL_4["parsed_output"]
        email_1 = test_regular_user.create_job_email()
        email_2 = test_admin_user.create_job_email()

        result_1 = service.save_job_base_info_to_db(session, email_record=email_1, job_results=jobs)
        result_2 = service.save_job_base_info_to_db(session, email_record=email_2, job_results=jobs)

        # Verify separate job records were created for each owner
        assert len(result_1) == len(jobs)
        assert len(result_2) == len(jobs)
        assert result_1[0].id != result_2[0].id
        assert result_1[0].owner_id == test_regular_user.id
        assert result_2[0].owner_id == test_admin_user.id

        # Verify both have the same external job ID
        assert result_1[0].external_job_id == jobs[0].job_id
        assert result_2[0].external_job_id == jobs[0].job_id

        # Verify total count in the database
        total_jobs = session.query(models.ScrapedJob).count()
        assert total_jobs == len(jobs) * 2


class TestUpdateScrapedJobData:
    """Test class for JobScraper.update_scraped_job_data method"""

    def test_save_job_data_single_job_and_data(self, test_regular_user: FixtureUser, session: Session) -> None:
        """Test saving job data to a single job record"""
        service = JobEmailScrapingService()

        email_data = resources.LINKEDIN_EMAIL_3
        jobs = email_data["parsed_output"]

        sample_scraped_job = test_regular_user.create_scraped_job(
            external_job_id=jobs[0].job_id,
            platform=email_data["platform"],
            company="Initial Company Name",
            salary_min=40000.0,
        )

        # Verify initial state
        assert sample_scraped_job.status == ProcessingStatus.PENDING
        assert sample_scraped_job.title is None
        assert sample_scraped_job.company == "Initial Company Name"

        sample_job_data = {
            "company": None,
            "location": "London, UK",
            "job": {
                "title": "Senior Software Engineer",
                "description": "We are looking for a senior software engineer to join our team...",
                "url": "https://example.com/job/123",
                "salary": {"min_amount": 50000.0, "max_amount": 70000.0},
            },
            "raw": "<html>Raw job posting HTML content</html>",
        }

        # Save job data
        service.update_scraped_job_data(
            session, job_record=sample_scraped_job, job_result=JobResult.model_validate(sample_job_data)
        )

        # Refresh the record from database
        session.refresh(sample_scraped_job)

        # Verify the data was saved correctly
        assert sample_scraped_job.status == ProcessingStatus.COMPLETED
        job_data = sample_job_data["job"]
        assert isinstance(job_data, dict)
        assert sample_scraped_job.company == "Initial Company Name"  # not overwritten
        assert sample_scraped_job.title == job_data["title"]
        assert sample_scraped_job.description == job_data["description"]
        assert sample_scraped_job.salary_min == job_data["salary"]["min_amount"]  # overwritten
        assert sample_scraped_job.salary_max == job_data["salary"]["max_amount"]


# ----------------------------------------------------- RUN METHODS ----------------------------------------------------


class TestExtractEmailData:
    """Test suite for the extract_email_data method."""

    EmailRecordFactory = Callable[..., tuple[models.JobEmail, list]]

    def test_linkedin_email_jobs_success(
        self, session: Session, email_record_factory: EmailRecordFactory, test_toast_user_1: FixtureUser
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""
        service = JobEmailScrapingService()

        email_entry, expected_jobs = email_record_factory("linkedin_3", test_toast_user_1)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry.platform
        assert len(platform_stat.job_found_ids) == len(expected_jobs)

        # Verify service log
        service_log = session.query(models.JobEmailScrapingServiceLog).first()
        assert service_log
        assert service_log.job_found_n == len(expected_jobs)

        # Verify service errors
        service_error = session.query(models.ServiceError).first()
        assert service_error is None

        # Verify email record updated
        email_record = session.query(models.JobEmail).filter(models.JobEmail.id == email_entry.id).first()
        assert email_record
        assert email_record.job_found_n == len(expected_jobs)

    def test_indeed_email_jobs_success(
        self, session: Session, email_record_factory: EmailRecordFactory, test_toast_user_1: FixtureUser
    ) -> None:
        """Test successful processing of Indeed email jobs."""
        service = JobEmailScrapingService()

        email_entry, expected_jobs = email_record_factory("indeed_3", test_toast_user_1)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry.platform
        assert len(platform_stat.job_found_ids) == len(expected_jobs)

        # Verify email record updated
        email_record = session.query(models.JobEmail).filter(models.JobEmail.id == email_entry.id).first()
        assert email_record
        assert email_record.job_found_n == len(expected_jobs)

    def test_veganjobs_email_jobs_success(
        self, session: Session, email_record_factory: EmailRecordFactory, test_toast_user_1: FixtureUser
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""
        service = JobEmailScrapingService()

        email_entry, expected_jobs = email_record_factory("veganjobs_3", test_toast_user_1)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry.platform
        assert len(platform_stat.job_found_ids) == len(expected_jobs)

        # Verify email record updated
        email_record = session.query(models.JobEmail).filter(models.JobEmail.id == email_entry.id).first()
        assert email_record
        assert email_record.job_found_n == len(expected_jobs)

    def test_nhs_email_jobs_success(
        self, session: Session, email_record_factory: EmailRecordFactory, test_toast_user_1: FixtureUser
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""
        service = JobEmailScrapingService()

        email_entry, expected_jobs = email_record_factory("nhs_3", test_toast_user_1)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry.platform
        assert len(platform_stat.job_found_ids) == len(expected_jobs)

        # Verify email record updated
        email_record = session.query(models.JobEmail).filter(models.JobEmail.id == email_entry.id).first()
        assert email_record
        assert email_record.job_found_n == len(expected_jobs)

    def test_linkedin_email_jobs_success_duplicates_different_owners(
        self,
        session: Session,
        email_record_factory: EmailRecordFactory,
        test_toast_user_1: FixtureUser,
        test_toast_user_2: FixtureUser,
    ) -> None:
        """Test processing of LinkedIn email job ids for different owners but same data"""
        service = JobEmailScrapingService()

        email_entry_1, expected_jobs = email_record_factory("linkedin_3", test_toast_user_1)
        email_entry_2, expected_jobs = email_record_factory("linkedin_3", test_toast_user_2)
        service.extract_email_data(session, email_record=email_entry_1, service_log=email_entry_1.service_log)
        service.extract_email_data(session, email_record=email_entry_2, service_log=email_entry_2.service_log)

        # Check that each use has a copy of the jobs
        scraped_jobs = (
            session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry_1.owner_id).all()
        )
        assert len(scraped_jobs) == len(expected_jobs)
        scraped_jobs = (
            session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry_2.owner_id).all()
        )
        assert len(scraped_jobs) == len(expected_jobs)

        # Check that the jobs unique record
        assert session.query(models.ScrapedJob).distinct(models.ScrapedJob.external_job_id).count() == len(
            expected_jobs
        )

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry_1.platform
        assert len(platform_stat.job_found_ids) == len(expected_jobs) * 2  # counted for both users

    def test_linkedin_email_jobs_success_duplicates_same_owner(
        self, session: Session, email_record_factory: EmailRecordFactory, test_toast_user_1: FixtureUser
    ) -> None:
        """Test successful processing of LinkedIn email for the same user with duplicate job ids"""
        service = JobEmailScrapingService()

        email_entry, expected_job_ids = email_record_factory("linkedin_3", test_toast_user_1)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)
        service.extract_email_data(session, email_record=email_entry, service_log=email_entry.service_log)

        # Verify jobs saved in database without duplicates
        scraped_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)  # did not save the duplicates

        # Verify platform stats updated
        platform_stat = session.query(models.JobEmailScrapingPlatformStat).first()
        assert platform_stat
        assert platform_stat.name == email_entry.platform
        assert len(platform_stat.job_found_ids) == len(expected_job_ids)  # did not save the duplicates


class TestProcessEmails:
    """Test class for JobScraper.process_emails method"""

    def test_single_user(
        self,
        session: Session,
        test_toast_user_1: FixtureUser,
        test_toast_user_2: FixtureUser,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""
        service = JobEmailScrapingService()

        # Mock get_email_ids to return emails only for the first user
        with patch.object(service, "get_email_ids") as mock_get_email_ids:

            email_id = "linkedin_3_" + str(test_toast_user_1.email)
            email = resources.TEST_EMAILS[email_id]

            def mock_get_email_ids_side_effect(
                recipient_email: str = "",
                sender_email: str = "",
                inbox: str = "INBOX",
                timedelta_days: int | float = 1,
                subject_contains: str = "",
                from_email: list[str] | str = "",
                to_email: str = "",
            ) -> list[str]:
                """Mock get_email_ids to return emails only for the first user"""
                _ = recipient_email, inbox, timedelta_days, from_email, to_email, subject_contains
                return [email_id] if sender_email == test_toast_user_1.email else []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            service.process_emails(session, timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            assert len(test_job_scraping_service_log.user_processed_ids) == 2

            # Verify the platform stats
            platform_stat = (
                session.query(models.JobEmailScrapingPlatformStat)
                .filter(models.JobEmailScrapingPlatformStat.name == email["platform"])
                .first()
            )
            assert platform_stat is not None
            assert len(platform_stat.email_saved_ids) == 1
            assert len(platform_stat.email_skipped_ids) == 0
            assert len(platform_stat.job_found_ids) == len(email["parsed_output"])
            assert len(platform_stat.job_scrape_succeeded_ids) == 0
            assert len(platform_stat.job_scrape_failed_ids) == 0

            # Verify service log errors
            service_log_error = session.query(models.ServiceError).first()
            assert service_log_error is None

            # Verify email was saved to database
            saved_emails = session.query(models.JobEmail).filter(models.JobEmail.external_email_id == email["id"]).all()
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == email["platform"]

            # Verify jobs were created only for the first user, not the second
            user1_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_1.id).all()
            )
            assert len(user1_jobs) == len(email["parsed_output"])
            user2_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_2.id).all()
            )
            assert len(user2_jobs) == 0

    def test_single_user_duplicate_jobs(
        self,
        session: Session,
        test_toast_user_1: FixtureUser,
        test_toast_user_2: FixtureUser,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""
        service = JobEmailScrapingService()

        # Mock get_email_ids to return the same email twice for the first user
        with patch.object(service, "get_email_ids") as mock_get_email_ids:

            email_id = "linkedin_3_" + str(test_toast_user_1.email)
            email = resources.TEST_EMAILS[email_id]

            def mock_get_email_ids_side_effect(
                recipient_email: str = "",
                sender_email: str = "",
                inbox: str = "INBOX",
                timedelta_days: int | float = 1,
                subject_contains: str = "",
                from_email: list[str] | str = "",
                to_email: str = "",
            ) -> list[str]:
                """Mock get_email_ids to return the same email twice for the first user"""
                _ = recipient_email, inbox, timedelta_days, from_email, to_email, subject_contains
                return [email_id, email_id] if sender_email == test_toast_user_1.email else []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            service.process_emails(session, timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            assert len(test_job_scraping_service_log.user_processed_ids) == 2

            # Verify the platform stats
            platform_stat = (
                session.query(models.JobEmailScrapingPlatformStat)
                .filter(models.JobEmailScrapingPlatformStat.name == email["platform"])
                .first()
            )
            assert platform_stat is not None
            assert len(platform_stat.email_saved_ids) == 1
            assert len(platform_stat.email_skipped_ids) == 1
            assert len(platform_stat.job_found_ids) == len(email["parsed_output"])
            assert len(platform_stat.job_scrape_succeeded_ids) == 0
            assert len(platform_stat.job_scrape_failed_ids) == 0

            # Verify email was saved to database
            saved_emails = session.query(models.JobEmail).filter(models.JobEmail.external_email_id == email["id"]).all()
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == email["platform"]

            # Verify jobs were created only for the first user, not the second
            user1_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_1.id).all()
            )
            assert len(user1_jobs) == len(email["parsed_output"])
            user2_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_2.id).all()
            )
            assert len(user2_jobs) == 0

    def test_multiple_users_same_jobs(
        self,
        session: Session,
        test_toast_user_1: FixtureUser,
        test_toast_user_2: FixtureUser,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""
        service = JobEmailScrapingService()

        with patch.object(service, "get_email_ids") as mock_get_email_ids:

            email = resources.TEST_EMAILS["linkedin_3_" + str(test_toast_user_1.email)]

            # Setup mocks to return the platform email for each user, keyed by their address
            def mock_get_email_ids_side_effect(
                recipient_email: str = "",
                sender_email: str = "",
                inbox: str = "INBOX",
                timedelta_days: int | float = 1,
                subject_contains: str = "",
                from_email: list[str] | str = "",
                to_email: str = "",
            ) -> list[str]:
                """Mock function to return different emails for different users"""
                _ = recipient_email, inbox, timedelta_days, from_email, to_email, subject_contains
                if sender_email in (test_toast_user_1.email, test_toast_user_2.email):
                    return ["linkedin_3_" + sender_email]
                return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            service.process_emails(session, timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            n_job = len(email["parsed_output"])
            assert len(test_job_scraping_service_log.user_processed_ids) == 2

            # Verify the platform stats
            platform_stat = (
                session.query(models.JobEmailScrapingPlatformStat)
                .filter(models.JobEmailScrapingPlatformStat.name == email["platform"])
                .first()
            )
            assert platform_stat is not None
            assert len(platform_stat.email_saved_ids) == 2
            assert len(platform_stat.email_skipped_ids) == 0
            assert len(platform_stat.job_found_ids) == n_job * 2
            assert len(platform_stat.job_scrape_succeeded_ids) == 0
            assert len(platform_stat.job_scrape_failed_ids) == 0

            # Verify jobs were created for both users
            user1_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_1.id).all()
            )
            user2_jobs = (
                session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_toast_user_2.id).all()
            )
            assert len(user1_jobs) == n_job
            assert len(user2_jobs) == n_job


class TestScrapeJobs:
    """Test cases for the scrape_jobs method"""

    EmailRecordFactory = Callable[..., tuple[models.JobEmail, list]]

    @staticmethod
    def create_scraped_jobs(
        user: FixtureUser,
        email_record: models.JobEmail,
        jobs: list[JobResult],
    ) -> list[models.ScrapedJob]:
        """Create scraped jobs owned by the user, linked to the email and its service log."""

        return [
            user.create_scraped_job(
                emails=[email_record],
                service_log=email_record.service_log,
                external_job_id=job.job_id,
                title=job.job.title,
                platform=email_record.platform,
            )
            for job in jobs
        ]

    @pytest.fixture
    def indeed_scraped_jobs(
        self, test_toast_user_1: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> list[models.ScrapedJob]:
        """Indeed scraped jobs for the first user."""

        email_record, jobs = email_record_factory("indeed_3", test_toast_user_1)
        return self.create_scraped_jobs(test_toast_user_1, email_record, jobs)

    @pytest.fixture
    def indeed_scraped_jobs_user2(
        self, test_toast_user_2: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> list[models.ScrapedJob]:
        """Indeed scraped jobs for the second user (same job data as the first)."""

        email_record, jobs = email_record_factory("indeed_3", test_toast_user_2)
        return self.create_scraped_jobs(test_toast_user_2, email_record, jobs)

    @pytest.fixture
    def linkedin_scraped_jobs(
        self, test_toast_user_1: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> list[models.ScrapedJob]:
        """LinkedIn scraped jobs for the first user."""

        email_record, jobs = email_record_factory("linkedin_3", test_toast_user_1)
        return self.create_scraped_jobs(test_toast_user_1, email_record, jobs)

    @pytest.fixture
    def veganjobs_scraped_jobs(
        self, test_toast_user_1: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> list[models.ScrapedJob]:
        """VeganJobs scraped jobs for the first user."""

        email_record, jobs = email_record_factory("veganjobs_3", test_toast_user_1)
        return self.create_scraped_jobs(test_toast_user_1, email_record, jobs)

    @pytest.fixture
    def nhs_scraped_jobs(
        self, test_toast_user_1: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> list[models.ScrapedJob]:
        """NHS scraped jobs for the first user."""

        email_record, jobs = email_record_factory("nhs_3", test_toast_user_1)
        return self.create_scraped_jobs(test_toast_user_1, email_record, jobs)

    def test_indeed_success(
        self,
        indeed_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test successful scraping of Indeed email jobs"""
        service = JobEmailScrapingService()

        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.status == ProcessingStatus.COMPLETED

        # Verify the platform stats
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.INDEED.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == len(indeed_scraped_jobs)
        assert len(platform_stat.job_scrape_skipped_ids) == 0
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0

    def test_linkedin_success(
        self,
        linkedin_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test successful processing of LinkedIn email jobs"""
        service = JobEmailScrapingService()

        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.status == ProcessingStatus.COMPLETED

        # Verify the platform stats
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.LINKEDIN.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == len(linkedin_scraped_jobs)
        assert len(platform_stat.job_scrape_skipped_ids) == 0
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0

    def test_veganjobs_success(
        self,
        veganjobs_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test successful processing of VeganJobs email jobs"""
        service = JobEmailScrapingService()

        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.status == ProcessingStatus.COMPLETED

        # Verify the platform stats
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.VEGANJOBS.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == len(veganjobs_scraped_jobs)
        assert len(platform_stat.job_scrape_skipped_ids) == 0
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0

    def test_nhs_success(
        self,
        nhs_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test successful processing of NHS email jobs"""
        service = JobEmailScrapingService()

        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.status == ProcessingStatus.COMPLETED

        # Verify the platform stats
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.NHS.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == len(nhs_scraped_jobs)
        assert len(platform_stat.job_scrape_skipped_ids) == 0
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0

    def test_indeed_multiple_users_shared_jobs_success(
        self,
        indeed_scraped_jobs: list[models.ScrapedJob],
        indeed_scraped_jobs_user2: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test successful processing of Indeed email jobs with duplicated jobs for different users"""
        service = JobEmailScrapingService()

        # Create a mock for copy_existing_entry
        with patch.object(service, "copy_existing_entry", wraps=service.copy_existing_entry) as mock_copy:
            service.scrape_jobs(session, test_job_scraping_service_log)

            # Check how many times copy_existing_entry was called
            assert mock_copy.call_count == len(indeed_scraped_jobs_user2)

            # Verify all jobs are now scraped
            scraped_jobs = session.query(models.ScrapedJob).filter().all()
            assert len(scraped_jobs) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            assert session.query(models.ScrapedJob).filter(
                models.ScrapedJob.status == ProcessingStatus.COMPLETED
            ).count() == len(indeed_scraped_jobs)
            assert session.query(models.ScrapedJob).filter(
                models.ScrapedJob.status == ProcessingStatus.COPIED
            ).count() == len(indeed_scraped_jobs)

            # Verify the platform stats
            platform_stat = (
                session.query(models.JobEmailScrapingPlatformStat)
                .filter(models.JobEmailScrapingPlatformStat.name == Platform.INDEED.value)
                .first()
            )
            assert platform_stat is not None
            assert len(platform_stat.job_scrape_succeeded_ids) == len(indeed_scraped_jobs)
            assert len(platform_stat.job_scrape_skipped_ids) == 0
            assert len(platform_stat.job_scrape_failed_ids) == 0
            assert len(platform_stat.job_scrape_copied_ids) == len(indeed_scraped_jobs)

    def test_scraping_filter(
        self,
        nhs_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
        test_toast_user_1: FixtureUser,
    ) -> None:
        """Test successful processing of NHS email jobs with scraping filter applied"""
        service = JobEmailScrapingService()

        filter_entry = test_toast_user_1.create_scraping_exclusion_filter(
            type="title", operator="contains", value=nhs_scraped_jobs[0].title[:10]
        )
        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            if job.external_job_id == nhs_scraped_jobs[0].external_job_id:
                assert job.status == ProcessingStatus.FILTERED
                assert job.exclusion_filter_id == filter_entry.id
            else:
                assert job.status == ProcessingStatus.COMPLETED
                assert job.scraping_errors == []

        # Verify the platform stats
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.NHS.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == len(nhs_scraped_jobs) - 1
        assert len(platform_stat.job_scrape_filtered_ids) == 1
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0

    def test_monthly_quota_exceeded_skips_jobs(
        self,
        linkedin_scraped_jobs: list[models.ScrapedJob],
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Test that jobs are skipped when user exceeds monthly scrape quota"""
        service = JobEmailScrapingService()

        n = settings.monthly_scrape_quota + 100

        # Add a large number of scraped jobs
        for i in range(n):
            scraped_job = models.ScrapedJob(
                owner_id=linkedin_scraped_jobs[0].owner_id,
                external_job_id=str(i),
                status=ProcessingStatus.COMPLETED,
                platform="NotLinkedIn",
                service_log_id=test_job_scraping_service_log.id,
                scrape_datetime=dt.datetime.now(dt.timezone.utc),
            )
            session.add(scraped_job)
            session.commit()

        service.scrape_jobs(session, test_job_scraping_service_log)

        # Verify all jobs are skipped (not scraped)
        for job in linkedin_scraped_jobs:
            session.refresh(job)
            assert job.status == ProcessingStatus.SKIPPED
            assert job.skip_reason == f"Monthly scrape quota of {settings.monthly_scrape_quota} exceeded"

        # Verify the platform stats show jobs as skipped
        platform_stat = (
            session.query(models.JobEmailScrapingPlatformStat)
            .filter(models.JobEmailScrapingPlatformStat.name == Platform.LINKEDIN.value)
            .first()
        )
        assert platform_stat is not None
        assert len(platform_stat.job_scrape_succeeded_ids) == 0
        assert len(platform_stat.job_scrape_skipped_ids) == len(linkedin_scraped_jobs)
        assert len(platform_stat.job_scrape_failed_ids) == 0
        assert len(platform_stat.job_scrape_copied_ids) == 0


# ----------------------------------------------- SCRAPING RETRY LOGIC ------------------------------------------------


class TestScrapeJobsRetry:
    """Test cases for the retry mechanism in scrape_jobs"""

    EmailRecordFactory = Callable[..., tuple[models.JobEmail, list]]

    @pytest.fixture
    def indeed_scraped_job(
        self, test_toast_user_1: FixtureUser, email_record_factory: EmailRecordFactory
    ) -> models.ScrapedJob:
        """Create a single unprocessed Indeed scraped job"""

        email_record, jobs = email_record_factory("indeed_3", test_toast_user_1)
        return test_toast_user_1.create_scraped_job(
            emails=[email_record],
            service_log=email_record.service_log,
            external_job_id=jobs[0].job_id,
            platform=email_record.platform,
        )

    @staticmethod
    def _failing_scrapers() -> dict:
        """SCRAPERS dict where the Indeed scraper always raises an exception"""

        return {Platform.INDEED: partial(MockIndeedBrightdataJobScraper, simulate_exception=True)}

    def test_first_failure_schedules_retry(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """On first failure: retry_count=1, next_retry_at set, status still PENDING"""
        service = JobEmailScrapingService()

        with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
            service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 1
        assert indeed_scraped_job.scraping_next_retry_at is not None
        assert indeed_scraped_job.scraping_next_retry_at > dt.datetime.now(dt.timezone.utc)
        assert indeed_scraped_job.status == ProcessingStatus.PENDING
        assert len(indeed_scraped_job.scraping_errors) == 1
        assert indeed_scraped_job.scraping_errors[0].scraped_job_id == indeed_scraped_job.id
        assert (
            indeed_scraped_job.scraping_errors[0].job_email_scraping_service_log_id == test_job_scraping_service_log.id
        )

    def test_second_failure_increments_retry_count(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """On second failure: retry_count=2, still not permanently failed"""
        service = JobEmailScrapingService()

        for _ in range(2):
            indeed_scraped_job.scraping_next_retry_at = None  # make eligible for retry each run
            session.commit()
            with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
                service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 2
        assert indeed_scraped_job.status == ProcessingStatus.PENDING
        assert len(indeed_scraped_job.scraping_errors) == 2

    def test_third_failure_marks_permanently_failed(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """After 3 failures: status FAILED, retry_count=3"""
        service = JobEmailScrapingService()

        for _ in range(3):
            indeed_scraped_job.scraping_next_retry_at = None
            session.commit()
            with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
                service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 3
        assert indeed_scraped_job.status == ProcessingStatus.FAILED
        assert len(indeed_scraped_job.scraping_errors) == 3

    def test_future_retry_at_skips_job(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Job with next_retry_at in the future is not picked up for retry"""
        service = JobEmailScrapingService()

        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
        indeed_scraped_job.scraping_retry_count = 1
        session.commit()

        service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 1  # unchanged — was not attempted
        assert indeed_scraped_job.status == ProcessingStatus.PENDING

    def test_past_retry_at_triggers_retry(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """Job with next_retry_at in the past is picked up and retried successfully"""
        service = JobEmailScrapingService()

        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
        indeed_scraped_job.scraping_retry_count = 1
        session.commit()

        service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.status == ProcessingStatus.COMPLETED

    def test_successful_retry_after_two_failures(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """A job with 2 prior failures that succeeds on retry is processed, not failed"""
        service = JobEmailScrapingService()

        indeed_scraped_job.scraping_retry_count = 2
        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
        session.commit()

        # Success run — uses default mock (no simulate_exception)
        service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.status == ProcessingStatus.COMPLETED
        assert indeed_scraped_job.scraping_retry_count == 2  # unchanged on success

    def test_successful_retry_clears_next_retry_at(
        self,
        indeed_scraped_job: models.ScrapedJob,
        test_job_scraping_service_log: models.JobEmailScrapingServiceLog,
        session: Session,
    ) -> None:
        """A scheduled retry that succeeds must clear scraping_next_retry_at (regression test)."""
        service = JobEmailScrapingService()

        # Simulate a job that previously failed and has a retry scheduled in the past
        indeed_scraped_job.scraping_retry_count = 1
        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
        session.commit()

        # Success run — uses default mock (no simulate_exception)
        service.scrape_jobs(session, test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.status == ProcessingStatus.COMPLETED


# ----------------------------------------- FORWARDING EMAIL CONFIRMATION ----------------------------------------------


class TestExtractForwardingEmailConfirmation(BaseTest):
    """Test class for JobScraper.extract_forwarding_email_confirmation method"""

    FORWARDING_CONFIRMATION_URL = (
        "https://mail-settings.google.com/mail/vf-%5BANGjdJ8nH5EPXs18VsktRI5FvcVb%5D-YPBzzHEVNTIn"
    )
    FORWARDING_CANCELLATION_URL = "https://mail-settings.google.com/mail/uf-%5BANGjdJ8crp9rBh5i9I%5D-YPBzzHEVNTIn"

    def _make_forwarding_email(self, user_email: str, email_id: str = "fwd_confirm_1") -> EmailData:
        """Build a mock forwarding confirmation EmailData for a given gmail address."""
        return EmailData(
            id=email_id,
            message_id="",
            subject="Gmail Forwarding Confirmation",
            from_email="forwarding-noreply@google.com",
            to_email="jam.scraper@example.com",
            date=dt.datetime(2025, 1, 1),
            body=(
                f"{user_email} has requested to automatically forward mail to your email address "
                f"(jam.scraper@example.com). Please click the link below to confirm the request: "
                f"{self.FORWARDING_CONFIRMATION_URL} "
                f"If you accidentally clicked the link, cancel here: "
                f"{self.FORWARDING_CANCELLATION_URL} "
                f"For more information visit https://support.google.com/mail/bin/answer.py?answer=184973."
            ),
        )

    @staticmethod
    def _make_forwarding_email_no_link(user_email: str, email_id: str = "fwd_no_link_1") -> EmailData:
        """Build a mock forwarding EmailData without a valid confirmation link."""
        return EmailData(
            id=email_id,
            message_id="",
            subject="Gmail Forwarding Confirmation",
            from_email="forwarding-noreply@google.com",
            to_email="jam.scraper@example.com",
            date=dt.datetime(2025, 1, 1),
            body=f"{user_email} has requested to forward mail. No valid links here.",
        )

    def test_success_creates_confirmation_link(self, test_gmail_user: FixtureUser, session: Session) -> None:
        """Test successful extraction and saving of a forwarding confirmation link"""

        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id = "fwd_confirm_1"
        email_data = self._make_forwarding_email(test_gmail_user.email, email_id)

        with (
            patch.object(service, "get_email_ids", return_value=[email_id]) as mock_ids,
            patch.object(service, "get_email_data", return_value=email_data),
        ):
            service.extract_forwarding_email_confirmation(session, service_log)
            mock_ids.assert_called_once_with(from_email="forwarding-noreply@google.com", timedelta_days=1)

        # Verify confirmation link was created
        link = session.query(models.ForwardingConfirmationLink).first()
        assert link
        assert link.url == self.FORWARDING_CONFIRMATION_URL
        assert link.platform == "gmail"
        assert link.owner_id == test_gmail_user.id
        assert link.email_external_id == email_id
        assert link.is_used is False

    def test_skips_existing_entry(self, test_gmail_user: FixtureUser, session: Session) -> None:
        """Test that an already-processed email is skipped without creating duplicates"""

        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id = "fwd_confirm_existing"
        email_data = self._make_forwarding_email(test_gmail_user.email, email_id)

        # Pre-create an existing entry
        existing = models.ForwardingConfirmationLink(
            email_external_id=email_id,
            url="https://mail-settings.google.com/mail/vf-old",
            platform="gmail",
            owner_id=test_gmail_user.id,
        )
        session.add(existing)
        session.commit()

        with (
            patch.object(service, "get_email_ids", return_value=[email_id]),
            patch.object(service, "get_email_data", return_value=email_data) as mock_get_data,
        ):
            service.extract_forwarding_email_confirmation(session, service_log)
            # get_email_data should NOT be called since the entry already exists
            mock_get_data.assert_not_called()

        # Verify only the original entry exists
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 1

    def test_no_emails_found_logs_error(self, session: Session) -> None:
        """Test that when get_email_ids raises an exception, a service error is logged"""
        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        with patch.object(service, "get_email_ids", side_effect=Exception("IMAP error")):
            service.extract_forwarding_email_confirmation(session, service_log)

        # Verify a service error was logged
        errors = session.query(models.ServiceError).all()
        assert len(errors) == 1
        assert "Failed to get forwarding emails with platform gmail" in errors[0].message

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_no_link_in_body_skips(self, test_gmail_user: FixtureUser, session: Session) -> None:
        """Test that an email without a valid confirmation link is skipped"""
        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id = "fwd_no_link"
        email_data = self._make_forwarding_email_no_link(test_gmail_user.email, email_id)

        with (
            patch.object(service, "get_email_ids", return_value=[email_id]),
            patch.object(service, "get_email_data", return_value=email_data),
        ):
            service.extract_forwarding_email_confirmation(session, service_log)

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_user_not_found_skips(self, session: Session) -> None:
        """Test that when the gmail originator is not a registered user, the link is skipped"""
        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id = "fwd_unknown_user"
        email_data = self._make_forwarding_email("unknown_user@gmail.com", email_id)

        with (
            patch.object(service, "get_email_ids", return_value=[email_id]),
            patch.object(service, "get_email_data", return_value=email_data),
        ):
            service.extract_forwarding_email_confirmation(session, service_log)

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_multiple_emails_processed(self, test_gmail_user: FixtureUser, session: Session) -> None:
        """Test that multiple forwarding confirmation emails are all processed"""
        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id_1 = "fwd_multi_1"
        email_id_2 = "fwd_multi_2"
        email_data_1 = self._make_forwarding_email(test_gmail_user.email, email_id_1)
        email_data_2 = self._make_forwarding_email(test_gmail_user.email, email_id_2)

        def mock_get_email_data(eid: str) -> EmailData:
            """Mock get_email_data to return different EmailData objects for each email ID"""
            return {email_id_1: email_data_1, email_id_2: email_data_2}[eid]

        with (
            patch.object(service, "get_email_ids", return_value=[email_id_1, email_id_2]),
            patch.object(service, "get_email_data", side_effect=mock_get_email_data),
        ):
            service.extract_forwarding_email_confirmation(session, service_log)

        # Verify both confirmation links were created
        links = session.query(models.ForwardingConfirmationLink).all()
        assert len(links) == 2
        assert {link.email_external_id for link in links} == {email_id_1, email_id_2}

    def test_idempotent_on_rerun(self, test_gmail_user: FixtureUser, session: Session) -> None:
        """Test that running extraction twice does not create duplicate entries"""
        service = JobEmailScrapingService()
        service_log = self.create_email_scraping_service_log(session)

        email_id = "fwd_idempotent"
        email_data = self._make_forwarding_email(test_gmail_user.email, email_id)

        with (
            patch.object(service, "get_email_ids", return_value=[email_id]),
            patch.object(service, "get_email_data", return_value=email_data),
        ):
            service.extract_forwarding_email_confirmation(session, service_log)
            service.extract_forwarding_email_confirmation(session, service_log)

        # Verify only one confirmation link exists
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 1


class TestComputeLookbackDays(BaseTest):
    """Test class for JobEmailScrapingService.compute_lookback_days"""

    def test_first_run_uses_max(self, session: Session) -> None:
        """With no prior run, the window is the maximum."""
        service = JobEmailScrapingService()
        current = self.create_email_scraping_service_log(session, run_datetime=dt.datetime.now())
        assert service.compute_lookback_days(session, current, 1, 10) == 10

    def test_gap_within_bounds_uses_elapsed(self, session: Session) -> None:
        """A gap between the bounds returns the elapsed days."""
        service = JobEmailScrapingService()
        now = dt.datetime.now()
        self.create_email_scraping_service_log(session, run_datetime=now - dt.timedelta(days=4))
        current = self.create_email_scraping_service_log(session, run_datetime=now)
        assert service.compute_lookback_days(session, current, 1, 10) == pytest.approx(4, abs=1e-6)

    def test_small_gap_clamped_to_min(self, session: Session) -> None:
        """A gap below the minimum is clamped up to the minimum."""
        service = JobEmailScrapingService()
        now = dt.datetime.now()
        self.create_email_scraping_service_log(session, run_datetime=now - dt.timedelta(hours=3))
        current = self.create_email_scraping_service_log(session, run_datetime=now)
        assert service.compute_lookback_days(session, current, 1, 10) == 1

    def test_large_gap_clamped_to_max(self, session: Session) -> None:
        """A gap above the maximum is clamped down to the maximum."""
        service = JobEmailScrapingService()
        now = dt.datetime.now()
        self.create_email_scraping_service_log(session, run_datetime=now - dt.timedelta(days=30))
        current = self.create_email_scraping_service_log(session, run_datetime=now)
        assert service.compute_lookback_days(session, current, 1, 10) == 10

    def test_tour_runs_are_ignored(self, session: Session) -> None:
        """Tour runs are not treated as the previous run."""
        service = JobEmailScrapingService()
        now = dt.datetime.now()
        self.create_email_scraping_service_log(session, run_datetime=now - dt.timedelta(days=2))
        self.create_email_scraping_service_log(session, run_datetime=now - dt.timedelta(hours=1), is_tour=True)
        current = self.create_email_scraping_service_log(session, run_datetime=now)
        assert service.compute_lookback_days(session, current, 1, 10) == pytest.approx(2, abs=1e-6)
