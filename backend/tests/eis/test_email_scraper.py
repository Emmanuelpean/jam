"""Test module for email_parser.py functions and GmailScraper class"""

import datetime

import pytest

from app.eis import schemas
from app.eis.email_scraper import clean_email_address, get_user_id_from_email, GmailScraper
from app.eis.models import JobAlertEmail, EisServiceLog


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


class TestSaveEmailToDb:
    """Test class for GmailScraper.save_email_to_db method"""

    @pytest.fixture
    def email_data(self, test_users) -> schemas.JobAlertEmailCreate:
        """Create test email data"""

        return schemas.JobAlertEmailCreate(
            external_email_id="test_email_123",
            subject="Test Job Alert",
            sender=test_users[0].email,
            date_received=datetime.datetime(2024, 1, 15, 10, 30, 0),
            platform="LinkedIn",
            body="Test email body content",
        )

    @pytest.fixture
    def service_log(self, session) -> EisServiceLog:
        """Create a test service log"""

        # noinspection PyArgumentList
        service_log = EisServiceLog(
            name="test_service",
            run_datetime=datetime.datetime.now(),
            is_success=True,
        )
        session.add(service_log)
        session.commit()
        session.refresh(service_log)
        return service_log

    def test_save_new_email_success(self, email_data, service_log, session, test_users) -> None:
        """Test saving a new email successfully"""

        result_email, is_created = GmailScraper.save_email_to_db(email_data, service_log.id, session)

        assert is_created is True
        assert result_email.external_email_id == email_data.external_email_id
        assert result_email.subject == email_data.subject
        assert result_email.sender == email_data.sender
        assert result_email.platform == email_data.platform
        assert result_email.body == email_data.body
        assert result_email.owner_id == test_users[0].id
        assert result_email.service_log_id == service_log.id

        # Verify it's actually in the database
        # noinspection PyTypeChecker
        db_email = (
            session.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email_data.external_email_id).first()
        )
        assert db_email is not None
        assert db_email.id == result_email.id

    def test_save_existing_email_returns_existing(self, email_data, service_log, session, test_users) -> None:
        """Test that existing email is returned without creating a new record"""

        # noinspection PyArgumentList
        existing_email = JobAlertEmail(
            external_email_id=email_data.external_email_id,
            subject="Different Subject",
            sender="different@example.com",
            owner_id=test_users[0].id,
            service_log_id=service_log.id,
        )
        session.add(existing_email)
        session.commit()

        result_email, is_created = GmailScraper.save_email_to_db(email_data, service_log.id, session)

        assert is_created is False
        assert result_email.id == existing_email.id
        assert result_email.subject == "Different Subject"  # Original data preserved

        # Verify only one record exists
        # noinspection PyTypeChecker
        email_count = (
            session.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email_data.external_email_id).count()
        )
        assert email_count == 1


class TestExtractLinkedinJobIds:
    """Test class for GmailScraper.extract_linkedin_job_ids method"""

    @property
    def linkedin_email_body(self) -> str:
        """Load real LinkedIn email content"""

        with open("resources/linkedin_email.txt") as ofile:
            return ofile.read()

    def test_extract_linkedin_job_ids_real_email(self) -> None:
        """Test extracting LinkedIn job IDs from real LinkedIn email content"""

        job_ids = GmailScraper.extract_linkedin_job_ids(self.linkedin_email_body)

        expected_job_ids = [
            "4289870503",
            "4291891707",
            "4291383265",
            "4280354992",
            "4255584864",
            "4265877117"
        ]

        assert len(job_ids) == 6
        assert job_ids == expected_job_ids

        # Verify all expected job IDs are present
        for expected_id in expected_job_ids:
            assert expected_id in job_ids

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

    @pytest.mark.parametrize("url_pattern,expected_id", [
        ("https://www.linkedin.com/jobs/view/1234567890", "1234567890"),
        ("https://www.linkedin.com/comm/jobs/view/9876543210", "9876543210"),
        ("HTTPS://WWW.LINKEDIN.COM/JOBS/VIEW/5555555555", "5555555555"),
        ("https://linkedin.com/jobs/view/1111111111", "1111111111"),
        ("http://www.linkedin.com/jobs/view/2222222222", "2222222222"),
    ])
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

    @property
    def indeed_email_body(self) -> str:
        """Load real Indeed email content"""

        with open("resources/indeed_email.txt") as ofile:
            return ofile.read()

    def test_extract_indeed_job_ids_real_email(self) -> None:
        """Test extracting Indeed job IDs from real Indeed email content"""

        job_ids = GmailScraper.extract_indeed_job_ids(self.indeed_email_body)

        expected_job_ids = ['8799a57d87058103', 'd489097ca0fb185f', '7f9c701ebf265b69', '0537336f99ba1650',
                            '312725e138947a4b', '06498cad9de95b12', 'bd60005166216639', '42b107e214095d56',
                            'd30493c008b601e3', 'da413431a0c55ec7', '2ed37852402643ab', '14a9001ba6ebb965',
                            'eafb032fabcd77bc', '6838e604ddffd5ac', '227d4ccd0823fc96', '804b940d2d96b30b',
                            'f9aafc9ba4c31c6d', 'e034f0b761e410ea', '37cdb0ba59e12295', '7b272f46e4e46a14',
                            'd6110bfb54bdeddb', '5aa22054e7a8b76e', 'ae47862d410bbd39']

        assert job_ids == expected_job_ids

        # Verify all expected job IDs are present
        for expected_id in expected_job_ids:
            assert expected_id in job_ids

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

    @pytest.mark.parametrize("url_pattern,expected_id", [
        ("https://uk.indeed.com/rc/clk/dl?jk=1234567890abcdef&from=ja", "1234567890abcdef"),
        ("HTTPS://UK.INDEED.COM/RC/CLK/DL?JK=5555555555AAAA&FROM=JA", "5555555555AAAA"),
        ("http://indeed.com/rc/clk/dl?jk=1111111111bbbb&other=param", "1111111111bbbb"),
    ])
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
