"""Test module for email_scaper.py functions and JobScraper class"""

import datetime as dt
from unittest.mock import patch

import pytest

from app.eis.email_parsers import Platform
from app.eis.job_scrapers import JobResult
from app.eis.models import JobAlertEmail, ScrapedJob, PlatformStat, EisServiceLog
from tests.eis import resources
from tests.utils.table_data import TOAST_USER_1_INDEX


# ---------------------------------------------------- EMAIL METHODS ---------------------------------------------------


class TestSaveEmailToDb:
    """Test class for JobScraper.save_email_to_db method"""

    def test_save_new_email_success(self, test_job_scraper, test_users, test_service_log, session) -> None:
        """Test saving a new email successfully"""

        for email_id in resources.TEST_EMAILS:
            result_email, is_created = test_job_scraper.get_and_save_email_to_db(
                email_id, test_users[0], test_service_log.id
            )

            assert is_created
            assert result_email.external_email_id == email_id
            assert result_email.subject
            assert result_email.sender == resources.TEST_EMAILS[email_id]["to"]
            assert result_email.platform == resources.TEST_EMAILS[email_id]["platform"]
            assert result_email.body == resources.TEST_EMAILS[email_id]["body"]
            assert result_email.owner_id
            assert result_email.service_log_id == test_service_log.id

    def test_save_existing_email_returns_existing(
        self, test_job_scraper, test_service_log, session, test_users
    ) -> None:
        """Test that existing email is returned without creating a new record"""

        message_id = list(resources.TEST_EMAILS.keys())[0]

        # noinspection PyArgumentList
        existing_email = JobAlertEmail(
            external_email_id=message_id,
            subject="Different Subject",
            sender="different@example.com",
            owner_id=test_users[0].id,
            service_log_id=test_service_log.id,
            platform="indeed",
            date_received=dt.datetime.now(),
            body="Different body content",
        )
        session.add(existing_email)
        session.commit()

        # Try to save it with a different user
        result_email, is_created = test_job_scraper.get_and_save_email_to_db(
            message_id, test_users[1], test_service_log.id
        )

        assert is_created is False
        assert result_email.id == existing_email.id
        assert result_email.subject == "Different Subject"

        # Verify only one record exists
        email_count = session.query(JobAlertEmail).count()
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

        # Verify all jobs are ScrapedJob instances
        for job_record in result:
            assert job_record.owner_id == test_users[0].id
            assert job_record.external_job_id in [job.job_id for job in jobs]
            assert test_job_alert_emails[0] in job_record.emails

    def test_save_existing_jobs_returns_existing(
        self, test_job_scraper, test_job_alert_emails, session, test_users, test_service_log
    ) -> None:
        """Test that existing jobs are returned without creating duplicates"""

        email = resources.LINKEDIN_EMAIL_4
        jobs = email["parsed_output"]

        # Create existing jobs
        # noinspection PyArgumentList
        existing_job = ScrapedJob(
            external_job_id=jobs[0].job_id,
            owner_id=test_users[0].id,
            platform=email["platform"],
            service_log_id=test_service_log.id,
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
        total_jobs = session.query(ScrapedJob).count()
        assert total_jobs == len(jobs) * 2


class TestUpdateScrapedJobData:
    """Test class for JobScraper.update_scraped_job_data method"""

    def test_save_job_data_single_job_and_data(self, test_job_scraper, session, test_users, test_service_log) -> None:
        """Test saving job data to a single job record"""

        email = resources.LINKEDIN_EMAIL_3
        jobs = email["parsed_output"]

        # noinspection PyArgumentList
        sample_scraped_job = ScrapedJob(
            external_job_id=jobs[0].job_id,
            owner_id=test_users[0].id,
            platform=email["platform"],
            service_log_id=test_service_log.id,
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
        assert sample_scraped_job.company == "Initial Company Name"  # not overwritten
        assert sample_scraped_job.location_city == "London"
        assert sample_scraped_job.location_country == "United Kingdom"
        assert sample_scraped_job.title == sample_job_data["job"]["title"]
        assert sample_scraped_job.description == sample_job_data["job"]["description"]
        assert sample_scraped_job.salary_min == sample_job_data["job"]["salary"]["min_amount"]  # overwritten
        assert sample_scraped_job.salary_max == sample_job_data["job"]["salary"]["max_amount"]


# ----------------------------------------------------- RUN METHODS ----------------------------------------------------


class TestExtractEmailData:
    """Test suite for the extract_email_data method."""

    def test_linkedin_email_jobs_success(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        email_entry, expected_jobs = email_record_factory("linkedin_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(PlatformStat).first()
        assert platform_stat.name == email_entry.platform
        assert platform_stat.job_found_n == len(expected_jobs)
        assert platform_stat.job_failed_n == platform_stat.job_scraped_n == 0

        # Verify email record updated
        email_record = session.query(JobAlertEmail).filter(JobAlertEmail.id == email_entry.id).first()
        assert email_record.jobs_found_n == len(expected_jobs)

    def test_indeed_email_jobs_success(self, test_job_scraper, session, test_service_log, email_record_factory) -> None:
        """Test successful processing of Indeed email jobs."""

        email_entry, expected_jobs = email_record_factory("indeed_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(PlatformStat).first()
        assert platform_stat.name == email_entry.platform
        assert platform_stat.job_found_n == len(expected_jobs)
        assert platform_stat.job_failed_n == platform_stat.job_scraped_n == 0

        # Verify email record updated
        email_record = session.query(JobAlertEmail).filter(JobAlertEmail.id == email_entry.id).first()
        assert email_record.jobs_found_n == len(expected_jobs)

    def test_veganjobs_email_jobs_success(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_jobs = email_record_factory("veganjobs_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(PlatformStat).first()
        assert platform_stat.name == email_entry.platform
        assert platform_stat.job_found_n == len(expected_jobs)
        assert platform_stat.job_failed_n == platform_stat.job_scraped_n == 0

        # Verify email record updated
        email_record = session.query(JobAlertEmail).filter(JobAlertEmail.id == email_entry.id).first()
        assert email_record.jobs_found_n == len(expected_jobs)

    def test_nhs_email_jobs_success(self, test_job_scraper, session, test_service_log, email_record_factory) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_jobs = email_record_factory("nhs_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        # Verify jobs saved in database
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Verify platform stats updated
        platform_stat = session.query(PlatformStat).first()
        assert platform_stat.name == email_entry.platform
        assert platform_stat.job_found_n == len(expected_jobs)
        assert platform_stat.job_failed_n == platform_stat.job_scraped_n == 0

        # Verify email record updated
        email_record = session.query(JobAlertEmail).filter(JobAlertEmail.id == email_entry.id).first()
        assert email_record.jobs_found_n == len(expected_jobs)

    def test_linkedin_email_jobs_success_duplicates_different_owners(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test processing of LinkedIn email job ids for different owners but same data"""

        email_entry_1, expected_jobs = email_record_factory("linkedin_3", user_index=0)
        email_entry_2, expected_jobs = email_record_factory("linkedin_3", user_index=1)
        test_job_scraper.extract_email_data(email_record=email_entry_1, service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry_2, service_log_entry=test_service_log)

        # Check that each use has a copy of the jobs
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry_1.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry_2.owner_id).all()
        assert len(scraped_jobs) == len(expected_jobs)

        # Check that the jobs unique record
        assert session.query(ScrapedJob).distinct(ScrapedJob.external_job_id).count() == len(expected_jobs)

    def test_linkedin_email_jobs_success_duplicates_same_owner(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email for the same user with duplicate job ids"""

        email_entry, expected_job_ids = email_record_factory("linkedin_3", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        # Verify jobs saved in database without duplicates
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)


class TestProcessEmails:
    """Test class for JobScraper.process_emails method"""

    def test_single_user(self, test_job_scraper, session, test_users, test_service_log) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3" + "_" + str(test_users[0].email)
            email = resources.TEST_EMAILS[email_id]

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                _ = recipient_email, inbox_only, timedelta_days
                if sender_email == test_users[0].email:
                    return [email_id]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=1, service_log_entry=test_service_log)

            # Verify service log updates
            assert test_service_log.user_processed_n == 3
            assert test_service_log.email_found_n == 1
            assert test_service_log.email_saved_n == 1
            assert test_service_log.email_skipped_n == 0

            # Verify the platform stats
            platform_stat = session.query(PlatformStat).filter(PlatformStat.name == email["platform"]).first()
            assert platform_stat is not None
            assert platform_stat.email_saved_n == 1
            assert platform_stat.email_skipped_n == 0
            assert platform_stat.job_found_n == len(email["parsed_output"])
            assert platform_stat.job_scraped_n == 0
            assert platform_stat.job_failed_n == 0

            # Verify email was saved to database
            saved_emails = session.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email["id"]).all()
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == email["platform"]

            # Verify jobs were created only for the first user
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(email["parsed_output"])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

    def test_single_user_duplicate_jobs(self, test_job_scraper, session, test_users, test_service_log) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3" + "_" + str(test_users[0].email)
            email = resources.TEST_EMAILS[email_id]

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                _ = recipient_email, inbox_only, timedelta_days
                if sender_email == test_users[0].email:
                    return [email_id, email_id]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=1, service_log_entry=test_service_log)

            # Verify service log updates
            assert test_service_log.user_processed_n == 3
            assert test_service_log.email_found_n == 2
            assert test_service_log.email_saved_n == 1
            assert test_service_log.email_skipped_n == 1

            # Verify the platform stats
            platform_stat = session.query(PlatformStat).filter(PlatformStat.name == email["platform"]).first()
            assert platform_stat is not None
            assert platform_stat.email_saved_n == 1
            assert platform_stat.email_skipped_n == 1
            assert platform_stat.job_found_n == len(email["parsed_output"])
            assert platform_stat.job_scraped_n == 0
            assert platform_stat.job_failed_n == 0

            # Verify email was saved to database
            saved_emails = session.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email["id"]).all()
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == email["platform"]

            # Verify jobs were created only for the first user
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(email["parsed_output"])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

    def test_multiple_users_same_jobs(
        self,
        test_job_scraper,
        session,
        test_users,
        test_service_log,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "linkedin_3"
            email = resources.TEST_EMAILS[email_id + "_" + str(test_users[0].email)]

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock function to return different emails for different users"""
                _ = recipient_email, inbox_only, timedelta_days
                if sender_email == test_users[0].email:
                    return [email_id + "_" + str(test_users[0].email)]
                elif sender_email == test_users[TOAST_USER_1_INDEX].email:
                    return [email_id + "_" + str(test_users[TOAST_USER_1_INDEX].email)]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=2, service_log_entry=test_service_log)

            # Verify service log updates
            n_job = len(email["parsed_output"])
            assert test_service_log.user_processed_n == 3
            assert test_service_log.email_found_n == 2
            assert test_service_log.email_saved_n == 2

            # Verify the platform stats
            platform_stat = session.query(PlatformStat).filter(PlatformStat.name == email["platform"]).first()
            assert platform_stat is not None
            assert platform_stat.email_saved_n == 2
            assert platform_stat.email_skipped_n == 0
            assert platform_stat.job_found_n == n_job * 2
            assert platform_stat.job_scraped_n == 0
            assert platform_stat.job_failed_n == 0

            # Verify jobs were created for appropriate users
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            user2_jobs = (
                session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[TOAST_USER_1_INDEX].id).all()
            )
            assert len(user1_jobs) == n_job
            assert len(user2_jobs) == n_job


class TestScrapeJobs:
    """Test cases for the scrape_jobs method"""

    @staticmethod
    def create_scraped_jobs(
        session,
        email_record: JobAlertEmail,
        jobs: list[JobResult],
        test_service_log: EisServiceLog,
    ) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        scraped_jobs = []
        job_ids = [job.job_id for job in jobs]
        for job_id in job_ids:
            # noinspection PyArgumentList
            scraped_job = ScrapedJob(
                external_job_id=job_id,
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
    def indeed_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("indeed_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_service_log)

    @pytest.fixture
    def indeed_scraped_jobs_user2(
        self, test_users, session, email_record_factory, test_service_log
    ) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("indeed_3", user_index=3)
        return self.create_scraped_jobs(session, email_record, jobs, test_service_log)

    @pytest.fixture
    def linkedin_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("linkedin_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_service_log)

    @pytest.fixture
    def veganjobs_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("veganjobs_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_service_log)

    @pytest.fixture
    def nhs_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, jobs = email_record_factory("nhs_3", user_index=0)
        return self.create_scraped_jobs(session, email_record, jobs, test_service_log)

    def test_indeed_success(self, indeed_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful scraping of Indeed email jobs"""

        test_job_scraper.scrape_jobs(test_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped
            assert job.scrape_error is None

        # Verify the platform stats
        platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.INDEED.value).first()
        assert platform_stat is not None
        assert platform_stat.job_scraped_n == len(indeed_scraped_jobs)
        assert platform_stat.job_failed_n == 0

    def test_indeed_nobrightapi_success(
        self, indeed_scraped_jobs, test_service_log, job_scraper_with_brightapi_skip, session
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        job_scraper_with_brightapi_skip.scrape_jobs(test_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped
            assert job.scrape_error is None

        # Verify the platform stats
        platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.INDEED.value).first()
        assert platform_stat is not None
        assert platform_stat.job_scraped_n == len(indeed_scraped_jobs)
        assert platform_stat.job_failed_n == 0

    def test_linkedin_success(self, linkedin_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of LinkedIn email jobs"""

        test_job_scraper.scrape_jobs(test_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped
            assert job.scrape_error is None

        # Verify the platform stats
        platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.LINKEDIN.value).first()
        assert platform_stat is not None
        assert platform_stat.job_scraped_n == len(linkedin_scraped_jobs)
        assert platform_stat.job_failed_n == 0

    def test_veganjobs_success(self, veganjobs_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of VeganJobs email jobs"""

        test_job_scraper.scrape_jobs(test_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped
            assert job.scrape_error is None

        # Verify the platform stats
        platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.VEGANJOBS.value).first()
        assert platform_stat is not None
        assert platform_stat.job_scraped_n == len(veganjobs_scraped_jobs)
        assert platform_stat.job_failed_n == 0

    def test_nhs_success(self, nhs_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of NHS email jobs"""

        test_job_scraper.scrape_jobs(test_service_log)

        # Verify all jobs are now scraped
        scraped_jobs = session.query(ScrapedJob).filter().all()
        for job in scraped_jobs:
            assert job.is_scraped
            assert job.scrape_error is None

        # Verify the platform stats
        platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.NHS.value).first()
        assert platform_stat is not None
        assert platform_stat.job_scraped_n == len(nhs_scraped_jobs)
        assert platform_stat.job_failed_n == 0

    def test_indeed_multiple_users_shared_jobs_success(
        self, indeed_scraped_jobs, indeed_scraped_jobs_user2, test_service_log, test_job_scraper, session
    ) -> None:
        """Test successful processing of Indeed email jobs with duplicated jobs for different users"""

        # Create a mock for copy_existing_entry
        with patch.object(
            test_job_scraper,
            "copy_existing_entry",
            wraps=test_job_scraper.copy_existing_entry,
        ) as mock_copy:

            test_job_scraper.scrape_jobs(test_service_log)

            # Check how many times copy_existing_entry was called
            assert mock_copy.call_count == len(indeed_scraped_jobs_user2)

            # Verify all jobs are now scraped
            scraped_jobs = session.query(ScrapedJob).filter().all()
            assert len(scraped_jobs) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            for job in scraped_jobs:
                assert job.is_scraped
                assert not job.is_failed

            # Verify the platform stats
            platform_stat = session.query(PlatformStat).filter(PlatformStat.name == Platform.INDEED.value).first()
            assert platform_stat is not None
            assert platform_stat.job_scraped_n == len(indeed_scraped_jobs)
            assert platform_stat.job_copied_n == len(indeed_scraped_jobs_user2)
            assert platform_stat.job_failed_n == 0
