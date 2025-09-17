"""Test module for email_parser.py functions and GmailScraper class"""

import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.eis import schemas
from app.eis.email_scraper import clean_email_address, get_user_id_from_email, GmailScraper
from app.eis.job_scraper import extract_indeed_jobs_from_email
from app.eis.models import JobAlertEmail, ScrapedJob
from tests.conftest import open_file
from tests.eis.test_job_scraper import MockLinkedinJobScraper, MockIndeedJobScraper


# ------------------------------------------------------ FIXTURES ------------------------------------------------------


def create_gmail_scraper(**kwargs) -> GmailScraper:
    """Create a GmailScraper instance for testing with mocked file dependencies
    :param kwargs: keyword arguments passed to the GmailScraper constructor"""

    with (
        patch("builtins.open", create=True),
        patch("json.load") as mock_json_load,
        patch("os.path.exists") as mock_exists,
        patch("pickle.load"),
        patch("pickle.dump"),
        patch("app.eis.email_scraper.build") as mock_build,
    ):

        # Mock the secrets file reading
        mock_json_load.return_value = {
            "google_auth": {
                "installed": {
                    "client_id": "test_client_id.apps.googleusercontent.com",
                    "project_id": "test-project",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "test_client_secret",
                    "redirect_uris": ["http://localhost"],
                }
            }
        }

        # Mock token file doesn't exist (fresh authentication)
        mock_exists.return_value = False

        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the OAuth flow
        with patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_config") as mock_flow:
            mock_credentials = MagicMock()
            mock_credentials.valid = True
            mock_flow_instance = MagicMock()
            mock_flow_instance.run_local_server.return_value = mock_credentials
            mock_flow.return_value = mock_flow_instance

            # Create scraper with mocked dependencies
            scraper = GmailScraper(secrets_file="test_secrets.json", token_file="test_token.json", **kwargs)

            return scraper


@pytest.fixture
def gmail_scraper() -> GmailScraper:
    """Create a GmailScraper instance for testing with mocked file dependencies."""

    return create_gmail_scraper(skip_indeed_brightapi_scraping=False)


@pytest.fixture
def gmail_scraper_with_brightapi_skip() -> GmailScraper:
    """Create a GmailScraper instance with BrightAPI skip enabled."""

    return create_gmail_scraper(skip_indeed_brightapi_scraping=True)


def create_email_data(
    test_users,
    filename: str,
    platform: str,
    user_index: int,
) -> schemas.JobAlertEmailCreate:
    """Create a JobAlertEmailCreate data for testing
    :param test_users: test users
    :param filename: file name
    :param platform: platform name
    :param user_index: user index"""

    ofile = open_file(f"{filename}.txt")
    return schemas.JobAlertEmailCreate(
        external_email_id=f"{filename}_{platform}_{user_index}",
        subject="Subject",
        sender=test_users[user_index].email,
        date_received=datetime.datetime.now(),
        platform=platform,
        body=ofile,
    )


# Job ids extracted from the linkedin email body
LINKEDIN_JOB_IDS = [
    "4289870503",
    "4291891707",
    "4291383265",
    "4280354992",
    "4255584864",
    "4265877117",
]

# Job ids extracted from the indeed email body
INDEED_JOB_IDS = [
    "8799a57d87058103",
    "d489097ca0fb185f",
    "7f9c701ebf265b69",
    "0537336f99ba1650",
    "312725e138947a4b",
    "06498cad9de95b12",
    "bd60005166216639",
    "42b107e214095d56",
    "d30493c008b601e3",
    "da413431a0c55ec7",
    "2ed37852402643ab",
    "14a9001ba6ebb965",
    "eafb032fabcd77bc",
    "6838e604ddffd5ac",
    "227d4ccd0823fc96",
    "804b940d2d96b30b",
    "f9aafc9ba4c31c6d",
    "e034f0b761e410ea",
    "37cdb0ba59e12295",
    "7b272f46e4e46a14",
    "d6110bfb54bdeddb",
    "5aa22054e7a8b76e",
    "ae47862d410bbd39",
]


@pytest.fixture
def linkedin_email_data(test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create a LinkedIn job alert email record for testing."""

    return create_email_data(test_users, "linkedin_email", "linkedin", 0), LINKEDIN_JOB_IDS


@pytest.fixture
def linkedin_email_data_user2(test_users):
    """Create a LinkedIn job alert email record for testing."""

    return create_email_data(test_users, "linkedin_email", "linkedin", 1), LINKEDIN_JOB_IDS


@pytest.fixture
def indeed_email_data(test_users):
    """Create an Indeed job alert email record for testing."""

    return create_email_data(test_users, "indeed_email", "indeed", 0), INDEED_JOB_IDS


@pytest.fixture
def indeed_email_data_user2(session, test_users):
    """Create an Indeed job alert email record for testing."""

    return create_email_data(test_users, "indeed_email", "indeed", 1), INDEED_JOB_IDS


def create_email_record(session, test_users, filename: str, platform: str, user_index: int) -> JobAlertEmail:
    """Create a ScrapedJob record for testing.
    :param session: database session
    :param test_users: test users
    :param filename: file name
    :param platform: platform name
    :param user_index: user index"""

    email_data = create_email_data(test_users, filename, platform, user_index)
    # noinspection PyArgumentList
    email_record = JobAlertEmail(**email_data.model_dump(), owner_id=test_users[user_index].id)
    session.add(email_record)
    session.commit()
    return email_record


@pytest.fixture
def linkedin_email_record(session, test_users):
    """Create a LinkedIn job alert email record for testing."""

    return create_email_record(session, test_users, "linkedin_email", "linkedin", 0), LINKEDIN_JOB_IDS


@pytest.fixture
def linkedin_email_record_user2(session, test_users):
    """Create a LinkedIn job alert email record for testing."""

    return create_email_record(session, test_users, "linkedin_email", "linkedin", 1), LINKEDIN_JOB_IDS


@pytest.fixture
def indeed_email_record(session, test_users):
    """Create an Indeed job alert email record for testing."""

    return create_email_record(session, test_users, "indeed_email", "indeed", 0), INDEED_JOB_IDS


@pytest.fixture
def indeed_email_record_user2(session, test_users):
    """Create an Indeed job alert email record for testing."""

    return create_email_record(session, test_users, "indeed_email", "indeed", 1), INDEED_JOB_IDS


# --------------------------------------------------- BASE FUNCTIONS ---------------------------------------------------


class TestCleanEmailAddress:
    """Test class for clean_email_address function"""

    @pytest.mark.parametrize(
        "sender_field,expected",
        [
            ("John Doe <john.doe@gmail.com>", "john.doe@gmail.com"),
            ("john.doe@gmail.com", "john.doe@gmail.com"),
            ('"John Doe" <john.doe@gmail.com>', "john.doe@gmail.com"),
            ("Test User <TEST.USER@EXAMPLE.COM>", "test.user@example.com"),
            ("  test@example.com  ", "test@example.com"),
            ("Invalid Format", "invalid"),
            ("Jane Smith <jane.smith+tag@company.co.uk>", "jane.smith+tag@company.co.uk"),
            ("Multiple Words Name <multi.word@domain.org>", "multi.word@domain.org"),
        ],
    )
    def test_clean_email_address(self, sender_field, expected) -> None:
        """Test email address cleaning with various formats"""

        result = clean_email_address(sender_field)
        assert result == expected


class TestGetUserIdFromEmail:
    """Test class for get_user_id_from_email function"""

    def test_get_user_id_existing_user(self, session, test_users) -> None:
        """Test getting user ID for existing user"""

        test_user = test_users[0]
        result = get_user_id_from_email(test_user.email, session)
        assert result == test_user.id

    def test_get_user_id_non_existing_user(self, session) -> None:
        """Test getting user ID for non-existing user returns default ID 1"""

        with pytest.raises(AssertionError):
            get_user_id_from_email("nonexistent@example.com", session)

    def test_get_user_id_empty_email(self, session) -> None:
        """Test getting user ID with empty email"""

        with pytest.raises(AssertionError):
            get_user_id_from_email("", session)

    def test_get_user_id_case_sensitivity(self, session, test_users) -> None:
        """Test that email lookup is case-sensitive (as per database collation)"""

        test_user = test_users[0]
        upper_email = test_user.email.upper()
        with pytest.raises(AssertionError):
            get_user_id_from_email(upper_email, session)


# --------------------------------------------- GMAILSCRAPER STATIC METHODS --------------------------------------------


class TestSaveEmailToDb:
    """Test class for GmailScraper.save_email_to_db method"""

    def test_save_new_email_success(self, linkedin_email_data, test_service_logs, session, test_users) -> None:
        """Test saving a new email successfully"""

        linkedin_email_data = linkedin_email_data[0]
        result_email, is_created = GmailScraper.save_email_to_db(linkedin_email_data, test_service_logs[0].id, session)

        assert is_created is True
        assert result_email.external_email_id == linkedin_email_data.external_email_id
        assert result_email.subject == linkedin_email_data.subject
        assert result_email.sender == linkedin_email_data.sender
        assert result_email.platform == linkedin_email_data.platform
        assert result_email.body == linkedin_email_data.body
        assert result_email.owner_id == test_users[0].id
        assert result_email.service_log_id == test_service_logs[0].id

        # Verify it's actually in the database
        # noinspection PyTypeChecker
        db_email = (
            session.query(JobAlertEmail)
            .filter(JobAlertEmail.external_email_id == linkedin_email_data.external_email_id)
            .first()
        )
        assert db_email is not None
        assert db_email.id == result_email.id

    def test_save_existing_email_returns_existing(
        self, linkedin_email_data, test_service_logs, session, test_users
    ) -> None:
        """Test that existing email is returned without creating a new record"""

        # noinspection PyArgumentList
        existing_email = JobAlertEmail(
            external_email_id=linkedin_email_data[0].external_email_id,
            subject="Different Subject",
            sender="different@example.com",
            owner_id=test_users[0].id,
            service_log_id=test_service_logs[0].id,
        )
        session.add(existing_email)
        session.commit()

        result_email, is_created = GmailScraper.save_email_to_db(
            linkedin_email_data[0], test_service_logs[0].id, session
        )

        assert is_created is False
        assert result_email.id == existing_email.id
        assert result_email.subject == "Different Subject"  # Original data preserved

        # Verify only one record exists
        # noinspection PyTypeChecker
        email_count = (
            session.query(JobAlertEmail)
            .filter(JobAlertEmail.external_email_id == linkedin_email_data[0].external_email_id)
            .count()
        )
        assert email_count == 1


class TestExtractLinkedinJobIds:
    """Test class for GmailScraper.extract_linkedin_job_ids method"""

    def test_extract_linkedin_job_ids_real_email(self, linkedin_email_data) -> None:
        """Test extracting LinkedIn job IDs from real LinkedIn email content"""

        job_ids = GmailScraper.extract_linkedin_job_ids(linkedin_email_data[0].body)

        assert len(job_ids) == 6
        assert job_ids == LINKEDIN_JOB_IDS

    def test_extract_linkedin_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = GmailScraper.extract_linkedin_job_ids("")
        assert job_ids == []

    def test_extract_linkedin_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no LinkedIn job URLs"""

        body = """
        This is a test email with no LinkedIn job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.linkedin.com/profile/some-user
        But no job view URLs.
        """

        job_ids = GmailScraper.extract_linkedin_job_ids(body)
        assert job_ids == []

    @pytest.mark.parametrize(
        "url_pattern,expected_id",
        [
            ("https://www.linkedin.com/jobs/view/1234567890", "1234567890"),
            ("https://www.linkedin.com/comm/jobs/view/9876543210", "9876543210"),
            ("HTTPS://WWW.LINKEDIN.COM/JOBS/VIEW/5555555555", "5555555555"),
            ("https://linkedin.com/jobs/view/1111111111", "1111111111"),
            ("http://www.linkedin.com/jobs/view/2222222222", "2222222222"),
        ],
    )
    def test_extract_linkedin_job_ids_url_variations(self, url_pattern, expected_id) -> None:
        """Test extracting job IDs from various URL patterns"""

        body = f"Check out this job: {url_pattern}"

        job_ids = GmailScraper.extract_linkedin_job_ids(body)

        assert len(job_ids) == 1
        assert job_ids[0] == expected_id

    def test_extract_linkedin_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://www.linkedin.com/jobs/view/1111111111
        Job 2: https://www.linkedin.com/jobs/view/2222222222  
        Job 3: https://www.linkedin.com/jobs/view/1111111111
        Job 4: https://www.linkedin.com/jobs/view/3333333333
        Job 5: https://www.linkedin.com/jobs/view/2222222222
        """

        job_ids = GmailScraper.extract_linkedin_job_ids(body)

        assert len(job_ids) == 3
        assert job_ids == ["1111111111", "2222222222", "3333333333"]

    def test_extract_linkedin_job_ids_with_query_parameters(self) -> None:
        """Test extracting job IDs from URLs with query parameters (like the real email)"""

        body = """
        View job: https://www.linkedin.com/comm/jobs/view/4289870503/?trackingId=tt9C%2FzqOXzxRyy9uU5vDOw%3D%3D&refId=something
        Another job: https://www.linkedin.com/jobs/view/1234567890?ref=email&source=alert
        """

        job_ids = GmailScraper.extract_linkedin_job_ids(body)

        assert len(job_ids) == 2
        assert "4289870503" in job_ids
        assert "1234567890" in job_ids

    def test_extract_linkedin_job_ids_malformed_urls(self) -> None:
        """Test that malformed LinkedIn URLs are ignored"""

        body = """
        Good URL: https://www.linkedin.com/jobs/view/1111111111
        Malformed: https://www.linkedin.com/jobs/view/
        Malformed: https://www.linkedin.com/jobs/view/abcd
        Another good: https://www.linkedin.com/jobs/view/2222222222
        """

        job_ids = GmailScraper.extract_linkedin_job_ids(body)

        assert len(job_ids) == 2
        assert job_ids == ["1111111111", "2222222222"]


class TestExtractIndeedJobIds:
    """Test class for GmailScraper.extract_indeed_job_ids method"""

    def test_extract_indeed_job_ids_real_email(self, indeed_email_data) -> None:
        """Test extracting Indeed job IDs from real Indeed email content"""

        job_ids = GmailScraper.extract_indeed_job_ids(indeed_email_data[0].body)
        assert job_ids == INDEED_JOB_IDS

    def test_extract_indeed_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = GmailScraper.extract_indeed_job_ids("")
        assert job_ids == []

    def test_extract_indeed_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no Indeed job URLs"""

        body = """
        This is a test email with no Indeed job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.indeed.com/profile/some-user
        But no job view URLs.
        """

        job_ids = GmailScraper.extract_indeed_job_ids(body)
        assert job_ids == []

    @pytest.mark.parametrize(
        "url_pattern,expected_id",
        [
            ("https://uk.indeed.com/rc/clk/dl?jk=1234567890abcdef&from=ja", "1234567890abcdef"),
            ("HTTPS://UK.INDEED.COM/RC/CLK/DL?JK=5555555555AAAA&FROM=JA", "5555555555AAAA"),
            ("http://indeed.com/rc/clk/dl?jk=1111111111bbbb&other=param", "1111111111bbbb"),
        ],
    )
    def test_extract_indeed_job_ids_url_variations(self, url_pattern, expected_id) -> None:
        """Test extracting job IDs from various URL patterns"""

        body = f"Check out this job: {url_pattern}"

        job_ids = GmailScraper.extract_indeed_job_ids(body)

        assert len(job_ids) == 1
        assert job_ids[0] == expected_id

    def test_extract_indeed_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Job 2: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        Job 3: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Job 4: https://uk.indeed.com/rc/clk/dl?jk=3333333333ccc&from=ja
        Job 5: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        """

        job_ids = GmailScraper.extract_indeed_job_ids(body)

        assert len(job_ids) == 3
        assert job_ids == ["1111111111aaa", "2222222222bbb", "3333333333ccc"]

    def test_extract_indeed_job_ids_malformed_urls(self) -> None:
        """Test that malformed Indeed URLs are ignored"""

        body = """
        Good URL: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Malformed: https://uk.indeed.com/rc/clk/dl?from=ja
        Malformed: https://uk.indeed.com/rc/clk/dl?jk=
        Another good: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        """

        job_ids = GmailScraper.extract_indeed_job_ids(body)

        assert len(job_ids) == 2
        assert job_ids == ["1111111111aaa", "2222222222bbb"]


class TestSaveJobsToDb:
    """Test class for GmailScraper.save_jobs_to_db method"""

    def test_save_new_jobs_success(self, test_job_alert_emails, session, test_users) -> None:
        """Test saving new job IDs successfully"""

        job_ids = ["job_123", "job_456", "job_789"]

        result = GmailScraper.save_jobs_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids, db=session)

        # Verify returned list has correct length
        assert len(result) == 3

        # Verify all jobs are ScrapedJob instances
        for job_record in result:
            assert job_record.owner_id == test_users[0].id
            assert job_record.external_job_id in job_ids
            assert test_job_alert_emails[0] in job_record.emails

    def test_save_existing_jobs_returns_existing(self, test_job_alert_emails, session, test_users) -> None:
        """Test that existing jobs are returned without creating duplicates"""

        # Create existing jobs
        # noinspection PyArgumentList
        existing_job = ScrapedJob(external_job_id="existing_job_123", owner_id=test_users[0].id)
        session.add(existing_job)
        session.commit()
        session.refresh(existing_job)

        job_ids = ["existing_job_123", "new_job_456"]

        result = GmailScraper.save_jobs_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids, db=session)

        # Verify returned list has correct length
        assert len(result) == 2

    def test_save_jobs_different_owners(self, test_job_alert_emails, session, test_users) -> None:
        """Test that jobs with same external_job_id but different owners are created separately"""

        assert test_job_alert_emails[0].owner_id != test_job_alert_emails[-1].owner_id

        # Save same job ID for both users
        job_ids = ["same_job_123"]

        result_1 = GmailScraper.save_jobs_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids, db=session)

        result_2 = GmailScraper.save_jobs_to_db(email_record=test_job_alert_emails[-1], job_ids=job_ids, db=session)

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


class TestSaveJobDataToDb:
    """Test class for GmailScraper.save_job_data_to_db method"""

    @pytest.fixture
    def sample_job_data(self) -> dict:
        """Sample job data in the expected format"""

        return {
            "company": "Test Company Ltd",
            "location": "London, UK",
            "job": {
                "title": "Senior Software Engineer",
                "description": "We are looking for a senior software engineer to join our team...",
                "url": "https://example.com/job/123",
                "salary": {"min_amount": 50000.0, "max_amount": 70000.0},
            },
        }

    @pytest.fixture
    def sample_scraped_job(self, session, test_users) -> ScrapedJob:
        """Create a sample scraped job record"""

        # noinspection PyArgumentList
        job = ScrapedJob(
            external_job_id="test_job_123",
            owner_id=test_users[0].id,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job

    def test_save_job_data_single_job_and_data(self, sample_scraped_job, sample_job_data, session) -> None:
        """Test saving job data to a single job record"""

        # Verify initial state
        assert sample_scraped_job.is_scraped is False
        assert sample_scraped_job.title is None
        assert sample_scraped_job.company is None

        # Save job data
        GmailScraper.save_job_data_to_db(job_records=sample_scraped_job, job_data=sample_job_data, db=session, scraped_date=datetime.datetime.now())

        # Refresh the record from database
        session.refresh(sample_scraped_job)

        # Verify the data was saved correctly
        assert sample_scraped_job.is_scraped is True
        assert sample_scraped_job.company == sample_job_data["company"]
        assert sample_scraped_job.location == sample_job_data["location"]
        assert sample_scraped_job.title == sample_job_data["job"]["title"]
        assert sample_scraped_job.description == sample_job_data["job"]["description"]
        assert sample_scraped_job.url == sample_job_data["job"]["url"]
        assert sample_scraped_job.salary_min == sample_job_data["job"]["salary"]["min_amount"]
        assert sample_scraped_job.salary_max == sample_job_data["job"]["salary"]["max_amount"]

    def test_save_job_data_multiple_jobs_and_data(self, session, test_users) -> None:
        """Test saving job data to multiple job records"""

        # Create multiple job records
        # noinspection PyArgumentList
        job_1 = ScrapedJob(
            external_job_id="job_1",
            owner_id=test_users[0].id,
            is_scraped=False,
        )
        # noinspection PyArgumentList
        job_2 = ScrapedJob(
            external_job_id="job_2",
            owner_id=test_users[0].id,
            is_scraped=False,
        )
        session.add_all([job_1, job_2])
        session.commit()
        session.refresh(job_1)
        session.refresh(job_2)

        # Create multiple job data entries
        job_data_1 = {
            "company": "Company A",
            "location": "London, UK",
            "job": {
                "title": "Developer A",
                "description": "Description A",
                "url": "https://example.com/job/a",
                "salary": {"min_amount": 40000.0, "max_amount": 60000.0},
            },
        }

        job_data_2 = {
            "company": "Company B",
            "location": "Manchester, UK",
            "job": {
                "title": "Developer B",
                "description": "Description B",
                "url": "https://example.com/job/b",
                "salary": {"min_amount": 45000.0, "max_amount": 65000.0},
            },
        }

        # Save job data
        GmailScraper.save_job_data_to_db(job_records=[job_1, job_2], job_data=[job_data_1, job_data_2], db=session, scraped_date=datetime.datetime.now())

        # Refresh records
        session.refresh(job_1)
        session.refresh(job_2)

        # Verify first job
        assert job_1.is_scraped is True
        assert job_1.company == "Company A"
        assert job_1.title == "Developer A"
        assert job_1.salary_min == 40000.0
        assert job_1.salary_max == 60000.0

        # Verify second job
        assert job_2.is_scraped is True
        assert job_2.company == "Company B"
        assert job_2.title == "Developer B"
        assert job_2.salary_min == 45000.0
        assert job_2.salary_max == 65000.0


# ------------------------------------------------ GMAILSCRAPER METHODS ------------------------------------------------


class TestProcessEmailJobs:
    """Test suite for the _process_email_jobs method."""

    def test_process_linkedin_email_jobs_success(
        self,
        gmail_scraper,
        session,
        linkedin_email_record,
        test_service_logs,
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        gmail_scraper._process_email(
            db=session,
            email_record=linkedin_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        # noinspection PyTypeChecker
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(linkedin_email_record[1])

    def test_process_indeed_email_jobs_success(
        self,
        gmail_scraper,
        session,
        indeed_email_record,
        test_service_logs,
    ) -> None:
        """Test successful processing of Indeed email jobs."""

        gmail_scraper._process_email(
            db=session,
            email_record=indeed_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        # noinspection PyTypeChecker
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == indeed_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(indeed_email_record[1])

    def test_process_indeed_email_jobs_success_no_brightapi(
        self,
        gmail_scraper_with_brightapi_skip,
        session,
        indeed_email_record,
        test_service_logs,
    ) -> None:
        """Test successful processing of Indeed email jobs."""

        result = gmail_scraper_with_brightapi_skip._process_email(
            db=session,
            email_record=indeed_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        # noinspection PyTypeChecker
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == indeed_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(indeed_email_record[1])
        assert len(result) == len(indeed_email_record[1])

    def test_process_linkedin_email_jobs_success_duplicates_different_owners(
        self,
        gmail_scraper,
        session,
        linkedin_email_record,
        linkedin_email_record_user2,
        test_service_logs,
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        gmail_scraper._process_email(
            db=session,
            email_record=linkedin_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        gmail_scraper._process_email(
            db=session,
            email_record=linkedin_email_record_user2[0],
            service_log_entry=test_service_logs[0],
        )

        # noinspection PyTypeChecker
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(linkedin_email_record[1])
        # noinspection PyTypeChecker
        scraped_jobs = (
            session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record_user2[0].owner_id).all()
        )
        assert len(scraped_jobs) == len(linkedin_email_record_user2[1])

    def test_process_linkedin_email_jobs_success_duplicates_same_owner(
        self,
        gmail_scraper,
        session,
        linkedin_email_record,
        test_service_logs,
    ) -> None:
        """Test successful processing of LinkedIn email job ids"""

        gmail_scraper._process_email(
            db=session,
            email_record=linkedin_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        gmail_scraper._process_email(
            db=session,
            email_record=linkedin_email_record[0],
            service_log_entry=test_service_logs[0],
        )

        # noinspection PyTypeChecker
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(linkedin_email_record[1])


class TestProcessUserEmails:
    """Test class for GmailScraper._process_user_emails method"""

    def test_single_user(
        self,
        gmail_scraper,
        session,
        test_users,
        test_service_logs,
        linkedin_email_data,
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (
            patch.object(gmail_scraper, "get_email_ids") as mock_get_email_ids,
            patch.object(gmail_scraper, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                if user_email == test_users[0].email:
                    return [linkedin_email_data[0].external_email_id]
                else:
                    return []

            def mock_get_email_data_side_effect(_email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock get_email_data to return emails only for first user"""
                if user_email == test_users[0].email:
                    return linkedin_email_data[0]
                raise ValueError(f"Unexpected call for user {user_email}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            result = gmail_scraper._process_user_emails(
                db=session, timedelta_days=1, service_log_entry=test_service_logs[0]
            )

            # Verify service log updates
            assert test_service_logs[0].users_processed_n == len(test_users)
            assert test_service_logs[0].emails_found_n == 1
            assert test_service_logs[0].emails_saved_n == 1

            # Verify email was saved to database
            # noinspection PyTypeChecker
            saved_emails = (
                session.query(JobAlertEmail)
                .filter(JobAlertEmail.external_email_id == linkedin_email_data[0].external_email_id)
                .all()
            )
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == linkedin_email_data[0].platform

            # Verify jobs were created only for the first user
            # noinspection PyTypeChecker
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(linkedin_email_data[1])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                # noinspection PyTypeChecker
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

            # Verify empty result (no job data for LinkedIn without scraping)
            assert result == {}

    def test_multiple_users(
        self,
        gmail_scraper,
        session,
        test_users,
        test_service_logs,
        linkedin_email_data,
        indeed_email_data_user2,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (
            patch.object(gmail_scraper, "get_email_ids") as mock_get_email_ids,
            patch.object(gmail_scraper, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock get_email_ids() to return a list of email IDs for each user"""
                if user_email == test_users[0].email:
                    return [linkedin_email_data[0].external_email_id]
                elif user_email == test_users[1].email:
                    return [indeed_email_data_user2[0].external_email_id]
                return []

            def mock_get_email_data_side_effect(email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock get_email_data() to return the email data for each user"""
                if user_email == test_users[0].email:
                    return linkedin_email_data[0]
                elif user_email == test_users[1].email:
                    return indeed_email_data_user2[0]
                raise ValueError(f"Unexpected call for user {user_email} and email {email_id}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            gmail_scraper._process_user_emails(db=session, timedelta_days=2, service_log_entry=test_service_logs[0])

            # Verify service log updates
            assert test_service_logs[0].users_processed_n == len(test_users)
            assert test_service_logs[0].emails_found_n == 2
            assert test_service_logs[0].emails_saved_n == 2
            assert test_service_logs[0].linkedin_job_n == len(linkedin_email_data[1])
            assert test_service_logs[0].indeed_job_n == len(indeed_email_data_user2[1])
            assert test_service_logs[0].jobs_extracted_n == len(linkedin_email_data[1]) + len(
                indeed_email_data_user2[1]
            )

            # Verify jobs were created for appropriate users
            # noinspection PyTypeChecker
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            # noinspection PyTypeChecker
            user2_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[1].id).all()
            assert len(user1_jobs) == len(linkedin_email_data[1])
            assert len(user2_jobs) == len(indeed_email_data_user2[1])

            # Verify no jobs for remaining users (if any)
            for i in range(2, len(test_users)):
                # noinspection PyTypeChecker
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

    def test_multiple_users_same_jobs(
        self,
        gmail_scraper,
        session,
        test_users,
        test_service_logs,
        linkedin_email_data,
        linkedin_email_data_user2,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (
            patch.object(gmail_scraper, "get_email_ids") as mock_get_email_ids,
            patch.object(gmail_scraper, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock function to return different emails for different users"""
                if user_email == test_users[0].email:
                    return [linkedin_email_data[0].external_email_id]
                elif user_email == test_users[1].email:
                    return [linkedin_email_data_user2[0].external_email_id]
                return []

            def mock_get_email_data_side_effect(email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock method to return job data for a given email ID and user email"""
                if user_email == test_users[0].email:
                    return linkedin_email_data[0]
                elif user_email == test_users[1].email:
                    return linkedin_email_data_user2[0]
                raise ValueError(f"Unexpected call for user {user_email} and email {email_id}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            gmail_scraper._process_user_emails(db=session, timedelta_days=2, service_log_entry=test_service_logs[0])

            # Verify service log updates
            assert test_service_logs[0].users_processed_n == len(test_users)
            assert test_service_logs[0].emails_found_n == 2
            assert test_service_logs[0].emails_saved_n == 2
            assert test_service_logs[0].linkedin_job_n == len(linkedin_email_data[1]) + len(
                linkedin_email_data_user2[1]
            )
            assert test_service_logs[0].indeed_job_n == 0
            assert test_service_logs[0].jobs_extracted_n == len(linkedin_email_data[1]) + len(
                linkedin_email_data_user2[1]
            )

            # Verify jobs were created for appropriate users
            # noinspection PyTypeChecker
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            # noinspection PyTypeChecker
            user2_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[1].id).all()
            assert len(user1_jobs) == len(linkedin_email_data[1])
            assert len(user2_jobs) == len(linkedin_email_data_user2[1])

            # Verify no jobs for remaining users (if any)
            for i in range(2, len(test_users)):
                # noinspection PyTypeChecker
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

    def test_skip_brightdata(
        self,
        gmail_scraper_with_brightapi_skip,
        session,
        test_users,
        test_service_logs,
        indeed_email_data,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (
            patch.object(gmail_scraper_with_brightapi_skip, "get_email_ids") as mock_get_email_ids,
            patch.object(gmail_scraper_with_brightapi_skip, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock get_email_ids method to return emails only for first user"""
                if user_email == test_users[0].email:
                    return [indeed_email_data[0].external_email_id]
                return []

            def mock_get_email_data_side_effect(email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock get_email_data method to return email data only for first user"""
                if user_email == test_users[0].email:
                    return indeed_email_data[0]
                raise ValueError(f"Unexpected call for user {user_email} and email {email_id}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            result = gmail_scraper_with_brightapi_skip._process_user_emails(
                db=session, timedelta_days=2, service_log_entry=test_service_logs[0]
            )

            assert len(result) == 23


class TestScrapeRemainingJobs:
    """Test cases for the _scrape_remaining_jobs method"""

    @staticmethod
    def _scraped_jobs(session, email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        scraped_jobs = []
        owner_id = email_record[0].owner_id
        for job_id in email_record[1]:
            # noinspection PyArgumentList
            scraped_job = ScrapedJob(external_job_id=job_id, owner_id=owner_id)
            scraped_job.emails.append(email_record[0])
            session.add(scraped_job)
            scraped_jobs.append(scraped_job)
        session.commit()
        return scraped_jobs

    @pytest.fixture
    def indeed_scraped_jobs(self, test_users, session, indeed_email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, indeed_email_record)

    @pytest.fixture
    def indeed_scraped_jobs_user2(self, test_users, session, indeed_email_record_user2) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, indeed_email_record_user2)

    @pytest.fixture
    def linkedin_scraped_jobs(self, test_users, session, linkedin_email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, linkedin_email_record)

    def test_indeed_success(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        gmail_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(INDEED_JOB_IDS)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            gmail_scraper._scrape_remaining_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            unscraped_jobs_after = session.query(ScrapedJob).filter().all()
            for job in unscraped_jobs_after:
                assert job.is_scraped
                assert job.scrape_error is None

    def test_indeed_nobrightapi_success(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        gmail_scraper_with_brightapi_skip,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(INDEED_JOB_IDS)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            jobs = extract_indeed_jobs_from_email(indeed_scraped_jobs[0].emails[0].body)
            job_data = {}
            for job in jobs:
                job_ids = gmail_scraper_with_brightapi_skip.extract_indeed_job_ids(job["job"]["url"])
                if job_ids:  # Make sure we have at least one job ID
                    job_data[job_ids[0]] = job
            gmail_scraper_with_brightapi_skip._scrape_remaining_jobs(session, test_service_logs[0], job_data)

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

    def test_indeed_nobrightapi_fail(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        gmail_scraper_with_brightapi_skip,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(INDEED_JOB_IDS)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            gmail_scraper_with_brightapi_skip._scrape_remaining_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert job.is_failed

    def test_linkedin_success(
        self,
        linkedin_scraped_jobs,
        test_service_logs,
        gmail_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.LinkedinJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockLinkedinJobScraper(INDEED_JOB_IDS)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            gmail_scraper._scrape_remaining_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

    def test_indeed_multiple_users_shared_jobs_success(
        self,
        indeed_scraped_jobs,
        indeed_scraped_jobs_user2,
        test_service_logs,
        gmail_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""
        from unittest.mock import patch, MagicMock

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(INDEED_JOB_IDS)

            # Wrap the scrape_job method with a MagicMock to track calls
            original_scrape_job = mock_scraper_instance.scrape_job
            mock_scraper_instance.scrape_job = MagicMock(side_effect=original_scrape_job)

            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            gmail_scraper._scrape_remaining_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            assert len(jobs_after) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

            # Count how many times scrape_job() was called
            scrape_job_call_count = mock_scraper_instance.scrape_job.call_count
            assert scrape_job_call_count == len(indeed_scraped_jobs)
