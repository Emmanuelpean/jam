"""Test module for email_parser.py functions and GmailScraper class"""

import json
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

import pytest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

from app.eis.email_scraper import clean_email_address, get_user_id_from_email, GmailScraper, Email
from app.eis.models import JobAlertEmail, JobAlertEmailJob


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
        """Test that email lookup is case sensitive (as per database collation)"""

        test_user = test_users[0]
        upper_email = test_user.email.upper()
        with pytest.raises(AssertionError):
            get_user_id_from_email(upper_email, session)


class TestGmailScraper:
    """Test class for GmailScraper class"""

    @pytest.fixture
    def mock_credentials_config(self) -> dict:
        """Mock credentials configuration"""

        return {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }

    @pytest.fixture
    def mock_secrets_file_content(self, mock_credentials_config) -> str:
        """Mock secrets file content"""

        return json.dumps({"google_auth": mock_credentials_config})

    def test_init_with_default_parameters(self) -> None:
        """Test GmailScraper initialization with default parameters"""

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            assert scraper.token_file == "token.pickle"
            assert scraper.secrets_file == "eis_secrets.json"
            assert scraper.SCOPES == ["https://www.googleapis.com/auth/gmail.readonly"]

    def test_init_with_custom_parameters(self) -> None:
        """Test GmailScraper initialization with custom parameters"""

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper("custom_token.pickle", "custom_secrets.json")
            assert scraper.token_file == "custom_token.pickle"
            assert scraper.secrets_file == "custom_secrets.json"

    def test_load_credentials_success(self, mock_secrets_file_content, mock_credentials_config) -> None:
        """Test successful loading of credentials"""

        with patch("builtins.open", mock_open(read_data=mock_secrets_file_content)), patch.object(
            GmailScraper, "authenticate"
        ):
            scraper = GmailScraper()
            result = scraper._load_credentials()
            assert result == mock_credentials_config

    def test_load_credentials_file_not_found(self) -> None:
        """Test credentials loading when file doesn't exist"""

        with patch("builtins.open", side_effect=FileNotFoundError), patch.object(GmailScraper, "authenticate"):
            with pytest.raises(FileNotFoundError, match="Secrets file 'eis_secrets.json' not found"):
                GmailScraper()

    def test_load_credentials_invalid_json(self) -> None:
        """Test credentials loading with invalid JSON"""

        with patch("builtins.open", mock_open(read_data="invalid json")), patch.object(GmailScraper, "authenticate"):
            with pytest.raises(ValueError, match="Invalid JSON format"):
                GmailScraper()

    def test_load_credentials_missing_key(self) -> None:
        """Test credentials loading with missing google_auth key"""

        with patch("builtins.open", mock_open(read_data='{"other_key": "value"}')), patch.object(
            GmailScraper, "authenticate"
        ):
            with pytest.raises(ValueError, match="Invalid JSON format"):
                GmailScraper()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("pickle.dump")
    @patch("app.eis.email_scraper.build")
    def test_authenticate_with_existing_valid_token(
        self, mock_build, mock_pickle_dump, mock_pickle_load, _mock_file, mock_exists
    ) -> None:
        """Test authentication with existing valid token"""

        mock_exists.return_value = True
        mock_credentials = Mock(spec=Credentials)
        mock_credentials.valid = True
        mock_pickle_load.return_value = mock_credentials
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service

        with patch.object(GmailScraper, "_load_credentials", return_value={}):
            scraper = GmailScraper()

        assert scraper.service == mock_service
        mock_pickle_dump.assert_not_called()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("pickle.dump")
    @patch("app.eis.email_scraper.build")
    @patch("app.eis.email_scraper.Request")
    def test_authenticate_with_expired_token(
        self, _mock_request, mock_build, _mock_pickle_dump, mock_pickle_load, _mock_file, mock_exists
    ) -> None:
        """Test authentication with expired but refreshable token"""

        mock_exists.return_value = True
        mock_credentials = Mock(spec=Credentials)
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = "refresh_token"
        mock_pickle_load.return_value = mock_credentials
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service

        with patch.object(GmailScraper, "_load_credentials", return_value={}):
            scraper = GmailScraper()

        mock_credentials.refresh.assert_called_once()
        assert scraper.service == mock_service

    def test_search_messages_basic(self) -> None:
        """Test basic message search functionality"""

        mock_service = Mock()
        mock_result = {"messages": [{"id": "msg1"}, {"id": "msg2"}]}

        # Set up the mock chain properly
        mock_list_method = Mock()
        mock_list_method.execute.return_value = mock_result
        mock_service.users().messages().list.return_value = mock_list_method

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            scraper.service = mock_service

            result = scraper.search_messages("test@example.com", True, 1)

        assert result == ["msg1", "msg2"]
        # Check that the list method was called with correct parameters
        mock_service.users().messages().list.assert_called_once_with(
            userId="me", q="from:test@example.com in:inbox newer_than:1d"
        )

    def test_search_messages_no_results(self) -> None:
        """Test message search with no results"""
        mock_service = Mock()
        mock_result = {}
        mock_service.users().messages().list().execute.return_value = mock_result

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            scraper.service = mock_service

            result = scraper.search_messages("test@example.com")

        assert result == []

    def test_decode_base64(self) -> None:
        """Test base64 decoding functionality"""

        # Test data: "Hello World" encoded in base64 URL-safe format
        test_data = "SGVsbG8gV29ybGQ="
        expected = "Hello World"

        result = GmailScraper._decode_base64(test_data)
        assert result == expected

    def test_extract_body_plain_text(self) -> None:
        """Test email body extraction from plain text"""

        payload = {"mimeType": "text/plain", "body": {"data": "SGVsbG8gV29ybGQ="}}  # "Hello World" in base64

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            result = scraper._extract_body(payload)

        assert result == "Hello World"

    def test_extract_body_multipart(self) -> None:
        """Test email body extraction from multipart message"""

        payload = {
            "parts": [{"mimeType": "text/plain", "body": {"data": "SGVsbG8gV29ybGQ="}}]  # "Hello World" in base64
        }

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            result = scraper._extract_body(payload)

        assert result == "Hello World"

    def test_extract_linkedin_job_ids(self) -> None:
        """Test LinkedIn job ID extraction from email body"""

        body = """
        Check out these jobs:
        https://www.linkedin.com/jobs/view/123456789
        https://linkedin.com/comm/jobs/view/987654321
        https://www.linkedin.com/jobs/view/111222333
        https://www.linkedin.com/jobs/view/123456789  # duplicate
        """

        result = GmailScraper.extract_linkedin_job_ids(body)

        assert set(result) == {"123456789", "987654321", "111222333"}
        assert len(result) == 3  # duplicates removed

    def test_extract_indeed_job_ids(self) -> None:
        """Test Indeed job ID extraction from email body"""

        # Test with redirect URLs that the method actually expects
        body = """
        Check out these jobs:
        https://indeed.com/pagead/clk/dl?mo=r&ad=abc123def456&other=params
        https://uk.indeed.com/rc/clk/dl?jk=xyz789ghi012&more=params"""

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()

            def mock_redirect(url) -> str:
                """Mock redirect URL method to return URLs"""
                if "?mo" in url:
                    return "https://uk.indeed.com/viewjob?jk=XXX"
                return url

            with patch.object(scraper, "get_indeed_redirected_url", side_effect=mock_redirect):
                result = scraper.extract_indeed_job_ids(body)

        assert set(result) == {"XXX", "xyz789ghi012"}

    def test_get_message_data_linkedin(self) -> None:
        """Test getting message data for LinkedIn email"""

        mock_service = Mock()
        mock_message = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Job Alert"},
                    {"name": "From", "value": "John Doe <john@example.com>"},
                    {"name": "Date", "value": "Mon, 01 Jan 2024 12:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": "TGlua2VkSW4gam9iIGFsZXJ0"},  # "LinkedIn job alert" in base64
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_message

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            scraper.service = mock_service

            result = scraper.get_message_data("test_message_id")

        assert isinstance(result, Email)
        assert result.subject == "Job Alert"
        assert result.sender == "john@example.com"
        assert result.platform == "linkedin"
        assert result.external_email_id == "test_message_id"

    def test_get_message_data_invalid_platform(self) -> None:
        """Test getting message data with invalid platform"""

        mock_service = Mock()
        mock_message = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Job Alert"},
                    {"name": "From", "value": "john@example.com"},
                    {"name": "Date", "value": "Mon, 01 Jan 2024 12:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": "SW52YWxpZCBwbGF0Zm9ybQ=="},  # "Invalid platform" in base64
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_message

        with patch.object(GmailScraper, "_load_credentials"), patch.object(GmailScraper, "authenticate"):
            scraper = GmailScraper()
            scraper.service = mock_service

            with pytest.raises(ValueError, match="Email body does not contain a valid platform identifier"):
                scraper.get_message_data("test_message_id")

    def test_save_email_to_db_new_email(self, session, test_users, test_job_alert_emails) -> None:
        """Test saving new email to database"""

        test_user = test_users[0]
        email_data = self.get_test_email(test_user)

        result, is_new = GmailScraper.save_email_to_db(email_data, session)

        assert is_new is True
        assert isinstance(result, JobAlertEmail)
        assert result.external_email_id == "email_with_jobs"
        assert result.subject == "Job Alert"
        assert result.sender == test_user.email
        assert result.platform == "linkedin"
        assert result.owner_id == test_user.id

        # Verify it's actually in the database
        # noinspection PyTypeChecker
        db_email = session.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == "email_with_jobs").first()
        assert db_email.subject == "Job Alert"

    def test_save_email_to_db_existing_email(self, session, test_users, test_job_alert_emails) -> None:
        """Test saving an email that already exists in the database"""

        test_user = test_users[0]
        existing_email = test_job_alert_emails[0]  # Get the first existing email from test data

        # Create an Email object with the same external_email_id as an existing email
        email_data = Email(
            external_email_id=existing_email.external_email_id,  # Use same ID as existing email
            subject="Updated Subject",  # Different subject to show it won't update
            sender=test_user.email,
            date_received=datetime(2024, 2, 1, 15, 30, 0),  # Different date
            body="Updated body content",  # Different body
            platform="linkedin",
        )

        result, is_new = GmailScraper.save_email_to_db(email_data, session)

        # Should return the existing email record, not create a new one
        assert is_new is False
        assert isinstance(result, JobAlertEmail)
        assert result.id == existing_email.id  # Should be the same database record
        assert result.external_email_id == existing_email.external_email_id

        # The existing data should NOT be updated - original values should remain
        assert result.subject == existing_email.subject  # Original subject, not "Updated Subject"
        assert result.body == existing_email.body  # Original body, not "Updated body content"
        assert result.date_received == existing_email.date_received  # Original date
        assert result.owner_id == existing_email.owner_id

        # Verify the count hasn't changed
        total_emails = session.query(JobAlertEmail).count()
        expected_count = len(test_job_alert_emails)  # Should be same as initial test data
        assert total_emails == expected_count

    def test_save_email_to_db_nonexistent_user(self, session, test_users) -> None:
        """Test saving email for non-existent user (should use default user ID 1)"""

        with pytest.raises(AssertionError):
            email_data = self.get_test_email(test_users[0], sender="nonexistent@example.com")
            print(email_data)
            GmailScraper.save_email_to_db(email_data, session)

    @staticmethod
    def get_test_email(test_user, **kwargs) -> Email:
        """Helper method to create a test email
        :param test_user: User object to use as the sender
        :param kwargs: Additional keyword arguments to pass to the Email constructor"""

        # Create an email first
        params = dict(
            external_email_id="email_with_jobs",
            subject="Job Alert",
            sender=test_user.email,
            date_received=datetime(2024, 1, 1, 12, 0, 0),
            body="LinkedIn jobs here",
            platform="linkedin",
        )
        params.update(kwargs)
        return Email(**params)

    def test_save_job_ids_to_db(self, session, test_users) -> None:
        """Test saving job IDs to the database"""

        test_user = test_users[0]
        email_data = self.get_test_email(test_user)
        email_record = GmailScraper.save_email_to_db(email_data, session)[0]

        # Save job IDs
        job_ids = ["job123", "job456", "job789"]
        job_records = GmailScraper.save_job_to_db(email_record, job_ids, session)

        assert len(job_records) == 3

        # Verify all job records
        for i, job_record in enumerate(job_records):
            assert isinstance(job_record, JobAlertEmailJob)
            assert job_record.external_job_id == job_ids[i]
            assert job_record.owner_id == test_user.id
            assert job_record.email_id == email_record.id
            assert job_record.is_scraped is False

        # Verify they're in the database
        # noinspection PyTypeChecker
        db_jobs = session.query(JobAlertEmailJob).filter(JobAlertEmailJob.email_id == email_record.id).all()
        assert len(db_jobs) == 3
        assert set(job.external_job_id for job in db_jobs) == set(job_ids)

    def test_save_job_ids_to_db_duplicates(self, session, test_users) -> None:
        """Test saving duplicate job IDs doesn't create duplicates"""
        test_user = test_users[0]

        # Create an email first
        email_data = self.get_test_email(test_user)
        email_record, _ = GmailScraper.save_email_to_db(email_data, session)

        # Save job IDs first time
        job_ids = ["job123", "job456"]
        first_records = GmailScraper.save_job_to_db(email_record, job_ids, session)
        assert len(first_records) == 2

        # Try to save same job IDs again
        second_records = GmailScraper.save_job_to_db(email_record, job_ids, session)
        assert len(second_records) == 0  # No new records created

        # Verify total count is still 2
        # noinspection PyTypeChecker
        db_jobs = session.query(JobAlertEmailJob).filter(JobAlertEmailJob.email_id == email_record.id).all()
        assert len(db_jobs) == 2
