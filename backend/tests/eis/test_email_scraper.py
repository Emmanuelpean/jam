"""Test module for email_scaper.py functions and JobScraper class"""

import datetime as dt
from unittest.mock import patch

import pytest

from app.eis.email_parser import extract_indeed_job_ids
from app.eis.email_scraper import PLATFORMS
from app.eis.job_scraper import extract_indeed_jobs_from_email, JobResult
from app.eis.models import JobAlertEmail, ScrapedJob
from tests.eis import resources


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

        job_ids = ["job_123", "job_456", "job_789"]

        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        # Verify returned list has correct length
        assert len(result) == 3

        # Verify all jobs are ScrapedJob instances
        for job_record in result:
            assert job_record.owner_id == test_users[0].id
            assert job_record.external_job_id in job_ids
            assert test_job_alert_emails[0] in job_record.emails

    def test_save_existing_jobs_returns_existing(
        self, test_job_scraper, test_job_alert_emails, session, test_users, test_service_log
    ) -> None:
        """Test that existing jobs are returned without creating duplicates"""

        # Create existing jobs
        existing_job_id = "existing_job_123"
        # noinspection PyArgumentList
        existing_job = ScrapedJob(
            external_job_id=existing_job_id,
            owner_id=test_users[0].id,
            platform="linkedin",
            service_log_id=test_service_log.id,
        )
        session.add(existing_job)
        session.commit()
        session.refresh(existing_job)

        job_ids = [existing_job_id, "new_job_456"]

        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        # Verify returned list has correct length
        assert len(result) == 2

    def test_save_jobs_different_owners(self, test_job_scraper, test_job_alert_emails, session, test_users) -> None:
        """Test that jobs with same external_job_id but different owners are created separately"""

        assert test_job_alert_emails[0].owner_id != test_job_alert_emails[-1].owner_id

        # Save same job ID for both users
        job_ids = ["same_job_123"]

        result_1 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        result_2 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[-1], job_ids=job_ids)

        # Verify separate job records were created for each owner
        assert len(result_1) == 1
        assert len(result_2) == 1
        assert result_1[0].id != result_2[0].id
        assert result_1[0].owner_id == test_users[0].id
        assert result_2[0].owner_id == test_users[1].id

        # Verify both have the same external job ID
        assert result_1[0].external_job_id == "same_job_123"
        assert result_2[0].external_job_id == "same_job_123"

        # Verify total count in the database
        total_jobs = session.query(ScrapedJob).count()
        assert total_jobs == 2


class TestUpdateScrapedJobData:
    """Test class for JobScraper.update_scraped_job_data method"""

    def test_save_job_data_single_job_and_data(self, test_job_scraper, session, test_users, test_service_log) -> None:
        """Test saving job data to a single job record"""

        # noinspection PyArgumentList
        sample_scraped_job = ScrapedJob(
            external_job_id="test_job_123",
            owner_id=test_users[0].id,
            platform="indeed",
            service_log_id=test_service_log.id,
        )
        session.add(sample_scraped_job)
        session.commit()
        session.refresh(sample_scraped_job)

        # Verify initial state
        assert sample_scraped_job.is_scraped is False
        assert sample_scraped_job.title is None
        assert sample_scraped_job.company is None

        sample_job_data = {
            "company": "Test Company Ltd",
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
            job_record=sample_scraped_job, job_data=JobResult.model_validate(sample_job_data)
        )

        # Refresh the record from database
        session.refresh(sample_scraped_job)

        # Verify the data was saved correctly
        assert sample_scraped_job.is_scraped is True
        assert sample_scraped_job.company == sample_job_data["company"]
        assert sample_scraped_job.location_city == "London"
        assert sample_scraped_job.location_country == "United Kingdom"
        assert sample_scraped_job.title == sample_job_data["job"]["title"]
        assert sample_scraped_job.description == sample_job_data["job"]["description"]
        assert sample_scraped_job.salary_min == sample_job_data["job"]["salary"]["min_amount"]
        assert sample_scraped_job.salary_max == sample_job_data["job"]["salary"]["max_amount"]


# ----------------------------------------------------- RUN METHODS ----------------------------------------------------


class TestExtractEmailData:
    """Test suite for the extract_email_data method."""

    def test_linkedin_email_jobs_success(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        email_entry, expected_job_ids = email_record_factory("1", user_index=0)
        assert email_entry.platform == "linkedin"
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)

    def test_indeed_email_jobs_success(self, test_job_scraper, session, test_service_log, email_record_factory) -> None:
        """Test successful processing of Indeed email jobs."""

        with patch(
            "app.eis.email_scraper.extract_indeed_jobs_from_email",
            wraps=extract_indeed_jobs_from_email,
        ) as mock_extract:
            email_entry, expected_job_ids = email_record_factory("3", user_index=0)
            assert email_entry.platform == "indeed"
            test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

            mock_extract.assert_not_called()
            scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
            assert len(scraped_jobs) == len(expected_job_ids)

    def test_veganjobs_email_jobs_success(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_job_ids = email_record_factory("5", user_index=0)
        assert email_entry.platform == "veganjobs"
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)

    def test_nhs_email_jobs_success(self, test_job_scraper, session, test_service_log, email_record_factory) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry, expected_job_ids = email_record_factory("6", user_index=0)
        assert email_entry.platform == "nhs"
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)

    def test_indeed_email_jobs_success_no_brightapi(
        self, job_scraper_with_brightapi_skip, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of Indeed email jobs."""

        with patch(
            "app.eis.email_scraper.extract_indeed_jobs_from_email",
            wraps=extract_indeed_jobs_from_email,
        ) as mock_extract:
            email_entry, expected_job_ids = email_record_factory("3", user_index=0)
            assert email_entry.platform == "indeed"
            result = job_scraper_with_brightapi_skip.extract_email_data(
                email_record=email_entry, service_log_entry=test_service_log
            )

            mock_extract.assert_called_once()
            scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
            assert len(scraped_jobs) == len(expected_job_ids)
            assert len(result) == len(expected_job_ids)

    def test_linkedin_email_jobs_success_duplicates_different_owners(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test processing of LinkedIn email job ids for different owners but same data"""

        email_entry_1, expected_job_ids = email_record_factory("1", user_index=0)
        email_entry_2, expected_job_ids = email_record_factory("1", user_index=1)
        test_job_scraper.extract_email_data(email_record=email_entry_1, service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry_2, service_log_entry=test_service_log)

        # Check that each use has a copy of the jobs
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry_1.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry_2.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)

        # Check that the jobs unique record
        assert session.query(ScrapedJob).distinct(ScrapedJob.external_job_id).count() == len(expected_job_ids)

    def test_linkedin_email_jobs_success_duplicates_same_owner(
        self, test_job_scraper, session, test_service_log, email_record_factory
    ) -> None:
        """Test successful processing of LinkedIn email for the same user with duplicate job ids"""

        email_entry, expected_job_ids = email_record_factory("1", user_index=0)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(expected_job_ids)


class TestProcessEmails:
    """Test class for JobScraper.process_emails method"""

    def test_single_user(
        self,
        test_job_scraper,
        session,
        test_users,
        test_service_log,
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):

            email_id = "1" + "_" + str(test_users[0].email)

            # Setup mocks to be user-dependent
            # noinspection PyUnusedLocal
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""

                if sender_email == test_users[0].email:
                    return [email_id]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            result = test_job_scraper.process_emails(timedelta_days=1, service_log_entry=test_service_log)

            # Verify service log updates
            assert test_service_log.users_processed_n == 4
            assert test_service_log.emails_found_n == 1
            assert test_service_log.emails_saved_n == 1

            # Verify email was saved to database
            saved_emails = (
                session.query(JobAlertEmail)
                .filter(JobAlertEmail.external_email_id == resources.TEST_EMAILS[email_id]["id"])
                .all()
            )
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == resources.TEST_EMAILS[email_id]["platform"]

            # Verify jobs were created only for the first user
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(resources.TEST_EMAILS[email_id]["job_ids"])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

            # Verify empty result (no job data for LinkedIn without scraping)
            assert result == {"indeed": {}, "linkedin": {}, "veganjobs": {}, "nhs": {}}

    def test_multiple_users_same_jobs(
        self,
        test_job_scraper,
        session,
        test_users,
        test_service_log,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,):
            email_id = "1"

            # Setup mocks to return different emails for different users
            # noinspection PyUnusedLocal
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock function to return different emails for different users"""

                if sender_email == test_users[0].email:
                    return [email_id + "_" + str(test_users[0].email)]
                elif sender_email == test_users[3].email:
                    return [email_id + "_" + str(test_users[3].email)]
                else:
                    return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=2, service_log_entry=test_service_log)

            # Verify service log updates
            n_job = len(resources.TEST_EMAILS[email_id + "_" + str(test_users[0].email)]["job_ids"])
            assert test_service_log.users_processed_n == 4
            assert test_service_log.emails_found_n == 2
            assert test_service_log.emails_saved_n == 2
            assert test_service_log.linkedin_job_n == n_job * 2
            assert test_service_log.indeed_job_n == 0
            assert test_service_log.jobs_extracted_n == n_job * 2

            # Verify jobs were created for appropriate users
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            user2_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[3].id).all()
            assert len(user1_jobs) == n_job
            assert len(user2_jobs) == n_job

    def test_skip_brightdata(
        self,
        job_scraper_with_brightapi_skip,
        session,
        test_users,
        test_service_log,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (patch.object(job_scraper_with_brightapi_skip, "get_email_ids") as mock_get_email_ids,):

            email_id = "3" + "_" + str(test_users[0].email)
            assert resources.TEST_EMAILS[email_id]["platform"] == "indeed"

            # Setup mocks to return different emails for different users
            # noinspection PyUnusedLocal
            def mock_get_email_ids_side_effect(recipient_email, sender_email, inbox_only, timedelta_days) -> list[str]:
                """Mock get_email_ids method to return emails only for first user"""

                if sender_email == test_users[0].email:
                    return [email_id]
                return []

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect

            # Call the method
            result = job_scraper_with_brightapi_skip.process_emails(2, test_service_log)

            assert len(result["indeed"]) == len(resources.TEST_EMAILS[email_id]["job_ids"])


class TestScrapeJobs:
    """Test cases for the scrape_jobs method"""

    @staticmethod
    def _scraped_jobs(session, email_record, job_ids, test_service_log) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        scraped_jobs = []
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

        email_record, job_ids = email_record_factory("3", user_index=0)
        return self._scraped_jobs(session, email_record, job_ids, test_service_log)

    @pytest.fixture
    def indeed_scraped_jobs_user2(
        self, test_users, session, email_record_factory, test_service_log
    ) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, job_ids = email_record_factory("3", user_index=3)
        assert email_record.platform == "indeed"
        return self._scraped_jobs(session, email_record, job_ids, test_service_log)

    @pytest.fixture
    def linkedin_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        email_record, job_ids = email_record_factory("1", user_index=0)
        assert email_record.platform == "linkedin"
        return self._scraped_jobs(session, email_record, job_ids, test_service_log)

    @pytest.fixture
    def veganjobs_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, job_ids = email_record_factory("5", user_index=0)
        assert email_record.platform == "veganjobs"
        return self._scraped_jobs(session, email_record, job_ids, test_service_log)

    @pytest.fixture
    def nhs_scraped_jobs(self, test_users, session, email_record_factory, test_service_log) -> list[ScrapedJob]:
        """Fixture to create VeganJobs scraped jobs for multiple users"""

        email_record, job_ids = email_record_factory("6", user_index=0)
        assert email_record.platform == "nhs"
        return self._scraped_jobs(session, email_record, job_ids, test_service_log)

    def test_indeed_success(self, indeed_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of Indeed email jobs"""

        test_job_scraper.scrape_jobs(test_service_log, {})

        # Verify all jobs are now scraped
        unscraped_jobs_after = session.query(ScrapedJob).filter().all()
        for job in unscraped_jobs_after:
            assert job.is_scraped
            assert job.scrape_error is None

    def test_indeed_nobrightapi_success(
        self, indeed_scraped_jobs, test_service_log, job_scraper_with_brightapi_skip, session
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        # Extract the job data from the email body
        jobs = extract_indeed_jobs_from_email(indeed_scraped_jobs[0].emails[0].body)
        job_data = {key: {} for key in PLATFORMS}
        for job in jobs:
            job_ids = extract_indeed_job_ids(job.job.url)
            if job_ids:
                job_data["indeed"][job_ids[0]] = job
        job_scraper_with_brightapi_skip.scrape_jobs(test_service_log, job_data)

        # Verify all jobs are now scraped
        jobs_after = session.query(ScrapedJob).filter().all()
        for job in jobs_after:
            assert job.is_scraped
            assert not job.is_failed

    def test_linkedin_success(self, linkedin_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of LinkedIn email jobs"""

        test_job_scraper.scrape_jobs(test_service_log, {})

        # Verify all jobs are now scraped
        jobs_after = session.query(ScrapedJob).filter().all()
        for job in jobs_after:
            assert job.is_scraped
            assert not job.is_failed

    def test_veganjobs_success(self, veganjobs_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of VeganJobs email jobs"""

        test_job_scraper.scrape_jobs(test_service_log, {})

        # Verify all jobs are now scraped
        jobs_after = session.query(ScrapedJob).filter().all()
        for job in jobs_after:
            assert job.is_scraped
            assert not job.is_failed

    def test_nhs_success(self, nhs_scraped_jobs, test_service_log, test_job_scraper, session) -> None:
        """Test successful processing of NHS email jobs"""

        test_job_scraper.scrape_jobs(test_service_log, {})

        # Verify all jobs are now scraped
        jobs_after = session.query(ScrapedJob).filter().all()
        for job in jobs_after:
            assert job.is_scraped
            assert not job.is_failed

    def test_indeed_multiple_users_shared_jobs_success(
        self, indeed_scraped_jobs, indeed_scraped_jobs_user2, test_service_log, test_job_scraper, session
    ) -> None:
        """Test successful processing of Indeed email jobs with duplicated jobs for different users"""

        # Create a mock for copy_existing_entry
        with patch.object(
            test_job_scraper, "copy_existing_entry", wraps=test_job_scraper.copy_existing_entry
        ) as mock_copy:
            test_job_scraper.scrape_jobs(test_service_log, {})

            # Check how many times copy_existing_entry was called
            assert mock_copy.call_count == len(indeed_scraped_jobs_user2)

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            assert len(jobs_after) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed
