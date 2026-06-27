"""Test module for email_scaper.py functions and JobScraper class"""

import datetime as dt
from functools import partial
from unittest import mock
from unittest.mock import patch

import pytest

from app import models
from app.config import settings
from app.emails.schemas import EmailData
from app.job_email_scraping.email_parsers.utils import Platform, remove_style_tags
from app.job_email_scraping.schemas import JobResult
from tests.job_email_scraping.mock_job_scrapers import MockIndeedBrightdataJobScraper
from tests.utils import job_email_resources as resources
from tests.utils.test_data import TOAST_USER_1_INDEX


# ---------------------------------------------------- EMAIL METHODS ---------------------------------------------------


class TestSaveEmailToDb:
    """Test class for JobScraper.save_email_to_db method"""

    def test_save_new_email_success(self, test_job_scraper, test_users, test_job_scraping_service_log, session) -> None:
        """Test saving a new email successfully"""

        for email_id in resources.TEST_EMAILS:
            result_email, is_created = test_job_scraper.get_and_save_email_to_db(
                email_id, test_users[0], test_job_scraping_service_log.id
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
            assert result_email.service_log_id == test_job_scraping_service_log.id

    def test_save_existing_email_returns_existing(
        self, test_job_scraper, test_job_scraping_service_log, session, test_users
    ) -> None:
        """Test that existing email is returned without creating a new record"""

        message_id = list(resources.TEST_EMAILS.keys())[0]

        existing_email = models.JobEmail(
            external_email_id=message_id,
            subject="Different Subject",
            sender="different@example.com",
            owner_id=test_users[0].id,
            service_log_id=test_job_scraping_service_log.id,
            platform="indeed",
            date_received=dt.datetime.now(),
            body="Different body content",
        )
        session.add(existing_email)
        session.commit()

        # Try to save it with a different user
        result_email, is_created = test_job_scraper.get_and_save_email_to_db(
            message_id, test_users[1], test_job_scraping_service_log.id
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

    def test_save_new_jobs_success(self, test_job_scraper, test_job_alert_emails, session, test_users) -> None:
        """Test saving new job IDs successfully"""

        jobs = resources.LINKEDIN_EMAIL_4_EXTRACTED
        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_results=jobs)

        # Verify returned list has correct length
        assert len(result) == len(jobs)

        # Verify all jobs are models.ScrapedJob instances
        for job_record in result:
            assert job_record.owner_id == test_users[0].id
            assert job_record.external_job_id in [job.job_id for job in jobs]
            assert test_job_alert_emails[0] in job_record.emails

    def test_save_existing_jobs_returns_existing(
        self, test_job_scraper, test_job_alert_emails, session, test_users, test_job_scraping_service_log
    ) -> None:
        """Test that existing jobs are returned without creating duplicates"""

        email = resources.LINKEDIN_EMAIL_4
        jobs = email["parsed_output"]

        # Create existing jobs
        existing_job = models.ScrapedJob(
            external_job_id=jobs[0].job_id,
            owner_id=test_users[0].id,
            platform=email["platform"],
            service_log_id=test_job_scraping_service_log.id,
        )
        session.add(existing_job)
        session.commit()
        session.refresh(existing_job)

        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_results=jobs)

        # Verify returned list has correct length
        assert len(result) == len(jobs)

    def test_save_jobs_different_owners(self, test_job_scraper, test_job_alert_emails, session, test_users) -> None:
        """Test that jobs with same external_job_id but different owners are created separately"""

        assert test_job_alert_emails[0].owner_id != test_job_alert_emails[-1].owner_id

        email = resources.LINKEDIN_EMAIL_4
        jobs = email["parsed_output"]

        result_1 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_results=jobs)
        result_2 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[-1], job_results=jobs)

        # Verify separate job records were created for each owner
        assert len(result_1) == len(jobs)
        assert len(result_2) == len(jobs)
        assert result_1[0].id != result_2[0].id
        assert result_1[0].owner_id == test_users[0].id
        assert result_2[0].owner_id == test_users[1].id

        # Verify both have the same external job ID
        assert result_1[0].external_job_id == jobs[0].job_id
        assert result_2[0].external_job_id == jobs[0].job_id

        # Verify total count in the database
        total_jobs = session.query(models.ScrapedJob).count()
        assert total_jobs == len(jobs) * 2


class TestUpdateScrapedJobData:
    """Test class for JobScraper.update_scraped_job_data method"""

    def test_save_job_data_single_job_and_data(
        self, test_job_scraper, session, test_users, test_job_scraping_service_log
    ) -> None:
        """Test saving job data to a single job record"""

        email = resources.LINKEDIN_EMAIL_3
        jobs = email["parsed_output"]

        sample_scraped_job = models.ScrapedJob(
            external_job_id=jobs[0].job_id,
            owner_id=test_users[0].id,
            platform=email["platform"],
            service_log_id=test_job_scraping_service_log.id,
            company="Initial Company Name",
            salary_min=40000.0,
        )
        session.add(sample_scraped_job)
        session.commit()
        session.refresh(sample_scraped_job)

        # Verify initial state
        assert sample_scraped_job.is_scraped is False
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
        test_job_scraper.update_scraped_job_data(
            job_record=sample_scraped_job, job_result=JobResult.model_validate(sample_job_data)
        )

        # Refresh the record from database
        session.refresh(sample_scraped_job)

        # Verify the data was saved correctly
        assert sample_scraped_job.is_scraped is True
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

    def test_linkedin_email_jobs_success(
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        email_entry, expected_jobs = email_record_factory("linkedin_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)

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
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test successful processing of Indeed email jobs."""

        email_entry, expected_jobs = email_record_factory("indeed_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)

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
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_jobs = email_record_factory("veganjobs_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)

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
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_jobs = email_record_factory("nhs_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)

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
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test processing of LinkedIn email job ids for different owners but same data"""

        email_entry_1, expected_jobs = email_record_factory("linkedin_3", user_index=0)
        email_entry_2, expected_jobs = email_record_factory("linkedin_3", user_index=1)
        test_job_scraper.extract_email_data(email_record=email_entry_1, service_log=test_job_scraping_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry_2, service_log=test_job_scraping_service_log)

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
        self, test_job_scraper, session, test_job_scraping_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email for the same user with duplicate job ids"""

        email_entry, expected_job_ids = email_record_factory("linkedin_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log=test_job_scraping_service_log)

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

    @staticmethod
    def get_premium_users(db) -> list[models.User]:
        """Return premium users list"""
        return db.query(models.User).filter(models.User.premium.has(is_active=True)).all()

    def test_single_user(self, test_job_scraper, session, test_users, test_job_scraping_service_log) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3" + "_" + str(test_users[0].email)
            email = resources.TEST_EMAILS[email_id]

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(
                recipient_email: str = "",
                sender_email: str = "",
                inbox: str = "INBOX",
                timedelta_days: int | float = 1,
                subject_contains: str = "",
                from_email: list[str] | str = "",
                to_email: str = "",
            ) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                _ = recipient_email, inbox, timedelta_days, from_email, to_email, subject_contains
                if sender_email == test_users[0].email:
                    return [email_id]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            assert len(test_job_scraping_service_log.user_processed_ids) == len(self.get_premium_users(session))

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

            # Verify jobs were created only for the first user
            user1_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(email["parsed_output"])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = (
                    session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_users[i].id).all()
                )
                assert len(user_jobs) == 0

    def test_single_user_duplicate_jobs(
        self, test_job_scraper, session, test_users, test_job_scraping_service_log
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3" + "_" + str(test_users[0].email)
            email = resources.TEST_EMAILS[email_id]

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(
                recipient_email: str = "",
                sender_email: str = "",
                inbox: str = "INBOX",
                timedelta_days: int | float = 1,
                subject_contains: str = "",
                from_email: list[str] | str = "",
                to_email: str = "",
            ) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                _ = recipient_email, inbox, timedelta_days, from_email, to_email, subject_contains
                if sender_email == test_users[0].email:
                    return [email_id, email_id]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            assert len(test_job_scraping_service_log.user_processed_ids) == len(self.get_premium_users(session))

            # Verify the platform stats
            platform_stat = (
                session.query(models.JobEmailScrapingPlatformStat)
                .filter(models.JobEmailScrapingPlatformStat.name == email["platform"])
                .first()
            )
            assert platform_stat is not None
            assert len(platform_stat.email_saved_ids) == 1
            assert len(platform_stat.email_skipped_ids) == 1
            assert len(platform_stat.email_saved_ids) == 1
            assert len(platform_stat.email_skipped_ids) == 1
            assert len(platform_stat.job_found_ids) == len(email["parsed_output"])
            assert len(platform_stat.job_scrape_succeeded_ids) == 0
            assert len(platform_stat.job_scrape_failed_ids) == 0

            # Verify email was saved to database
            saved_emails = session.query(models.JobEmail).filter(models.JobEmail.external_email_id == email["id"]).all()
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == email["platform"]

            # Verify jobs were created only for the first user
            user1_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(email["parsed_output"])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = (
                    session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_users[i].id).all()
                )
                assert len(user_jobs) == 0

    def test_multiple_users_same_jobs(
        self,
        test_job_scraper,
        session,
        test_users,
        test_job_scraping_service_log,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3"
            email = resources.TEST_EMAILS[email_id + "_" + str(test_users[0].email)]

            # Setup mocks to return different emails for different users
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
                if sender_email == test_users[0].email:
                    return [email_id + "_" + str(test_users[0].email)]
                elif sender_email == test_users[TOAST_USER_1_INDEX].email:
                    return [email_id + "_" + str(test_users[TOAST_USER_1_INDEX].email)]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=1, service_log=test_job_scraping_service_log)

            # Verify service log updates
            n_job = len(email["parsed_output"])
            assert len(test_job_scraping_service_log.user_processed_ids) == len(self.get_premium_users(session))

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

            # Verify jobs were created for appropriate users
            user1_jobs = session.query(models.ScrapedJob).filter(models.ScrapedJob.owner_id == test_users[0].id).all()
            user2_jobs = (
                session.query(models.ScrapedJob)
                .filter(models.ScrapedJob.owner_id == test_users[TOAST_USER_1_INDEX].id)
                .all()
            )
            assert len(user1_jobs) == n_job
            assert len(user2_jobs) == n_job


class TestScrapeJobs:
    """Test cases for the scrape_jobs method"""

    @staticmethod
    def create_scraped_jobs(
        session,
        email_record: models.JobEmail,
        jobs: list[JobResult],
        test_service_log: models.JobEmailScrapingServiceLog,
    ) -> list[models.ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        scraped_jobs = []
        for job in jobs:
            scraped_job = models.ScrapedJob(
                external_job_id=job.job_id,
                title=job.job.title,
                owner_id=email_record.owner_id,
                platform=email_record.platform,
                service_log_id=test_service_log.id,
            )
            scraped_job.emails.append(email_record)
            session.add(scraped_job)
            scraped_jobs.append(scraped_job)
        session.commit()
        return scraped_jobs

    @pytest.fixture
    def indeed_scraped_jobs(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> list[models.ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("indeed_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_job_scraping_service_log)

    @pytest.fixture
    def indeed_scraped_jobs_user2(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> list[models.ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("indeed_3", user_index=3)
        return self.create_scraped_jobs(session, email_record, jobs, test_job_scraping_service_log)

    @pytest.fixture
    def linkedin_scraped_jobs(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> list[models.ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("linkedin_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_job_scraping_service_log)

    @pytest.fixture
    def veganjobs_scraped_jobs(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> list[models.ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("veganjobs_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_job_scraping_service_log)

    @pytest.fixture
    def nhs_scraped_jobs(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> list[models.ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("nhs_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_job_scraping_service_log)

    def test_indeed_success(
        self, indeed_scraped_jobs, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Test successful scraping of Indeed email jobs"""

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped

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
        self, linkedin_scraped_jobs, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Test successful processing of LinkedIn email jobs"""

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped

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
        self, veganjobs_scraped_jobs, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Test successful processing of VeganJobs email jobs"""

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped

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

    def test_nhs_success(self, nhs_scraped_jobs, test_job_scraping_service_log, test_job_scraper, session) -> None:
        """Test successful processing of NHS email jobs"""

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped

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
        self, indeed_scraped_jobs, indeed_scraped_jobs_user2, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Test successful processing of Indeed email jobs with duplicated jobs for different users"""

        # Create a mock for copy_existing_entry
        with patch.object(
            test_job_scraper,
            "copy_existing_entry",
            wraps=test_job_scraper.copy_existing_entry,
        ) as mock_copy:

            test_job_scraper.scrape_jobs(test_job_scraping_service_log)

            # Check how many times copy_existing_entry was called
            assert mock_copy.call_count == len(indeed_scraped_jobs_user2)

            # Verify all jobs are now scraped
            scraped_jobs = session.query(models.ScrapedJob).filter().all()
            assert len(scraped_jobs) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            for job in scraped_jobs:
                assert job.is_scraped
                assert not job.is_failed

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

    def test_scraping_filter(self, nhs_scraped_jobs, test_job_scraping_service_log, test_job_scraper, session) -> None:
        """Test successful processing of NHS email jobs with scraping filter applied"""

        filter_entry = models.ScrapingExclusionFilter(
            type="title",
            operator="contains",
            value=nhs_scraped_jobs[0].title[:10],
            owner_id=nhs_scraped_jobs[0].owner_id,
        )
        session.add(filter_entry)
        session.commit()
        session.refresh(filter_entry)
        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(models.ScrapedJob).filter().all()
        for job in scraped_jobs:
            if job.external_job_id == nhs_scraped_jobs[0].external_job_id:
                assert not job.is_scraped
                assert job.exclusion_filter_id == filter_entry.id
            else:
                assert job.is_scraped

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
        linkedin_scraped_jobs,
        test_job_scraping_service_log,
        test_job_scraper,
        session,
        test_users,
    ) -> None:
        """Test that jobs are skipped when user exceeds monthly scrape quota"""

        n = settings.monthly_scrape_quota + 100

        # Add a large number of scraped jobs
        for i in range(n):
            scraped_job = models.ScrapedJob(
                owner_id=linkedin_scraped_jobs[0].owner_id,
                external_job_id=str(i),
                is_scraped=True,
                is_processed=True,
                is_failed=False,
                platform="NotLinkedIn",
                service_log_id=test_job_scraping_service_log.id,
                scrape_datetime=dt.datetime.now(dt.timezone.utc),
            )
            session.add(scraped_job)
            session.commit()

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        # Verify all jobs are skipped (not scraped)
        for job in linkedin_scraped_jobs:
            session.refresh(job)
            assert job.is_scraped is False
            assert job.is_skipped is True
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

    @pytest.fixture
    def indeed_scraped_job(
        self, test_users, session, email_record_factory, test_job_scraping_service_log
    ) -> models.ScrapedJob:
        """Create a single unprocessed Indeed scraped job"""

        email_record, jobs = email_record_factory("indeed_3", user_index=0)
        job = models.ScrapedJob(
            external_job_id=jobs[0].job_id,
            owner_id=email_record.owner_id,
            platform=email_record.platform,
            service_log_id=test_job_scraping_service_log.id,
        )
        job.emails.append(email_record)
        session.add(job)
        session.commit()
        return job

    @staticmethod
    def _failing_scrapers() -> dict:
        """SCRAPERS dict where the Indeed scraper always raises an exception"""

        return {Platform.INDEED: partial(MockIndeedBrightdataJobScraper, simulate_exception=True)}

    def test_first_failure_schedules_retry(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """On first failure: retry_count=1, next_retry_at set, is_processed=False, is_failed=False"""

        with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
            test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 1
        assert indeed_scraped_job.scraping_next_retry_at is not None
        assert indeed_scraped_job.scraping_next_retry_at > dt.datetime.now(dt.timezone.utc)
        assert indeed_scraped_job.is_processed is False
        assert indeed_scraped_job.is_failed is False
        service_errors = session.query(models.ServiceError).all()
        assert len(service_errors) == 1
        # The scrape error is linked to the ScrapedJob it failed on and the run it failed in
        assert service_errors[0].scraped_job_id == indeed_scraped_job.id
        assert service_errors[0].job_email_scraping_service_log_id == test_job_scraping_service_log.id

    def test_second_failure_increments_retry_count(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """On second failure: retry_count=2, still not permanently failed"""

        for _ in range(2):
            indeed_scraped_job.scraping_next_retry_at = None  # make eligible for retry each run
            session.commit()
            with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
                test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 2
        assert indeed_scraped_job.is_processed is False
        assert indeed_scraped_job.is_failed is False
        assert session.query(models.ServiceError).count() == 2

    def test_third_failure_marks_permanently_failed(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """After 3 failures: is_failed=True, is_processed=True, retry_count=3"""

        for _ in range(3):
            indeed_scraped_job.scraping_next_retry_at = None
            session.commit()
            with mock.patch("app.job_email_scraping.email_scraper.SCRAPERS", self._failing_scrapers()):
                test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 3
        assert indeed_scraped_job.is_processed is True
        assert indeed_scraped_job.is_failed is True
        assert session.query(models.ServiceError).count() == 3

    def test_future_retry_at_skips_job(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Job with next_retry_at in the future is not picked up for retry"""

        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
        indeed_scraped_job.scraping_retry_count = 1
        session.commit()

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.scraping_retry_count == 1  # unchanged — was not attempted
        assert indeed_scraped_job.is_processed is False

    def test_past_retry_at_triggers_retry(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """Job with next_retry_at in the past is picked up and retried successfully"""

        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
        indeed_scraped_job.scraping_retry_count = 1
        session.commit()

        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.is_scraped is True
        assert indeed_scraped_job.is_processed is True
        assert indeed_scraped_job.is_failed is False

    def test_successful_retry_after_two_failures(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """A job with 2 prior failures that succeeds on retry is processed, not failed"""

        indeed_scraped_job.scraping_retry_count = 2
        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
        session.commit()

        # Success run — uses default mock (no simulate_exception)
        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.is_scraped is True
        assert indeed_scraped_job.is_processed is True
        assert indeed_scraped_job.is_failed is False
        assert indeed_scraped_job.scraping_retry_count == 2  # unchanged on success

    def test_successful_retry_clears_next_retry_at(
        self, indeed_scraped_job, test_job_scraping_service_log, test_job_scraper, session
    ) -> None:
        """A scheduled retry that succeeds must clear scraping_next_retry_at (regression test)."""

        # Simulate a job that previously failed and has a retry scheduled in the past
        indeed_scraped_job.scraping_retry_count = 1
        indeed_scraped_job.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
        session.commit()

        # Success run — uses default mock (no simulate_exception)
        test_job_scraper.scrape_jobs(test_job_scraping_service_log)

        session.refresh(indeed_scraped_job)
        assert indeed_scraped_job.is_scraped is True
        assert indeed_scraped_job.is_processed is True
        # The retry window must be cleared so the job is not re-picked on the next run
        assert indeed_scraped_job.scraping_next_retry_at is None


# ----------------------------------------- FORWARDING EMAIL CONFIRMATION ----------------------------------------------


class TestExtractForwardingEmailConfirmation:
    """Test class for JobScraper.extract_forwarding_email_confirmation method"""

    GMAIL_USER_INDEX = 5
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
                f"For more information visit http://support.google.com/mail/bin/answer.py?answer=184973."
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

    def test_success_creates_confirmation_link(
        self, test_job_scraper, test_users, test_job_scraping_service_log, session
    ) -> None:
        """Test successful extraction and saving of a forwarding confirmation link"""

        gmail_user = test_users[self.GMAIL_USER_INDEX]
        email_id = "fwd_confirm_1"
        email_data = self._make_forwarding_email(gmail_user.email, email_id)

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id]) as mock_ids,
            patch.object(test_job_scraper, "get_email_data", return_value=email_data),
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)
            mock_ids.assert_called_once_with(from_email="forwarding-noreply@google.com", timedelta_days=1)

        # Verify confirmation link was created
        link = session.query(models.ForwardingConfirmationLink).first()
        assert link
        assert link.url == self.FORWARDING_CONFIRMATION_URL
        assert link.platform == "gmail"
        assert link.owner_id == gmail_user.id
        assert link.email_external_id == email_id
        assert link.is_used is False

    def test_skips_existing_entry(self, test_job_scraper, test_users, test_job_scraping_service_log, session) -> None:
        """Test that an already-processed email is skipped without creating duplicates"""

        gmail_user = test_users[self.GMAIL_USER_INDEX]
        email_id = "fwd_confirm_existing"
        email_data = self._make_forwarding_email(gmail_user.email, email_id)

        # Pre-create an existing entry
        existing = models.ForwardingConfirmationLink(
            email_external_id=email_id,
            url="https://mail-settings.google.com/mail/vf-old",
            platform="gmail",
            owner_id=gmail_user.id,
        )
        session.add(existing)
        session.commit()

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id]),
            patch.object(test_job_scraper, "get_email_data", return_value=email_data) as mock_get_data,
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)
            # get_email_data should NOT be called since the entry already exists
            mock_get_data.assert_not_called()

        # Verify only the original entry exists
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 1

    def test_no_emails_found_logs_error(self, test_job_scraper, test_job_scraping_service_log, session) -> None:
        """Test that when get_email_ids raises an exception, a service error is logged"""

        with patch.object(test_job_scraper, "get_email_ids", side_effect=Exception("IMAP error")):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)

        # Verify a service error was logged
        errors = session.query(models.ServiceError).all()
        assert len(errors) == 1
        assert "Failed to get email with platform gmail" in errors[0].message

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_no_link_in_body_skips(self, test_job_scraper, test_users, test_job_scraping_service_log, session) -> None:
        """Test that an email without a valid confirmation link is skipped"""

        gmail_user = test_users[self.GMAIL_USER_INDEX]
        email_id = "fwd_no_link"
        email_data = self._make_forwarding_email_no_link(gmail_user.email, email_id)

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id]),
            patch.object(test_job_scraper, "get_email_data", return_value=email_data),
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_user_not_found_skips(self, test_job_scraper, test_job_scraping_service_log, session) -> None:
        """Test that when the gmail originator is not a registered user, the link is skipped"""

        email_id = "fwd_unknown_user"
        email_data = self._make_forwarding_email("unknown_user@gmail.com", email_id)

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id]),
            patch.object(test_job_scraper, "get_email_data", return_value=email_data),
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)

        # Verify no confirmation links were created
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 0

    def test_multiple_emails_processed(
        self, test_job_scraper, test_users, test_job_scraping_service_log, session
    ) -> None:
        """Test that multiple forwarding confirmation emails are all processed"""

        gmail_user = test_users[self.GMAIL_USER_INDEX]
        email_id_1 = "fwd_multi_1"
        email_id_2 = "fwd_multi_2"
        email_data_1 = self._make_forwarding_email(gmail_user.email, email_id_1)
        email_data_2 = self._make_forwarding_email(gmail_user.email, email_id_2)

        def mock_get_email_data(eid: str) -> EmailData:
            """Mock get_email_data to return different EmailData objects for each email ID"""
            return {email_id_1: email_data_1, email_id_2: email_data_2}[eid]

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id_1, email_id_2]),
            patch.object(test_job_scraper, "get_email_data", side_effect=mock_get_email_data),
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)

        # Verify both confirmation links were created
        links = session.query(models.ForwardingConfirmationLink).all()
        assert len(links) == 2
        assert {link.email_external_id for link in links} == {email_id_1, email_id_2}

    def test_idempotent_on_rerun(self, test_job_scraper, test_users, test_job_scraping_service_log, session) -> None:
        """Test that running extraction twice does not create duplicate entries"""

        gmail_user = test_users[self.GMAIL_USER_INDEX]
        email_id = "fwd_idempotent"
        email_data = self._make_forwarding_email(gmail_user.email, email_id)

        with (
            patch.object(test_job_scraper, "get_email_ids", return_value=[email_id]),
            patch.object(test_job_scraper, "get_email_data", return_value=email_data),
        ):
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)
            test_job_scraper.extract_forwarding_email_confirmation(test_job_scraping_service_log)

        # Verify only one confirmation link exists
        count = session.query(models.ForwardingConfirmationLink).count()
        assert count == 1
