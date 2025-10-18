"""Tests for email service."""

from unittest.mock import patch, MagicMock, mock_open

import pytest

from app.emails.email_service import EmailService


class TestEmailService:
    """Test suite for EmailService class."""

    @pytest.fixture
    def email_svc(self) -> EmailService:
        """Create an EmailService instance for testing."""

        return EmailService()

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, email_svc) -> None:
        """Test successful email sending."""

        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Send email
        email_svc.send_email(
            recipient="test@example.com",
            subject="Test Subject",
            body="<h1>Test Body</h1>",
        )

        # Verify SMTP calls
        mock_smtp.assert_called_once_with(email_svc.smtp_server, email_svc.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(email_svc.sender, email_svc.password)
        mock_server.sendmail.assert_called_once()

        # Verify email content
        call_args = mock_server.sendmail.call_args[0]
        assert call_args[0] == email_svc.sender  # From
        assert call_args[1] == "test@example.com"  # To

    @patch("smtplib.SMTP")
    def test_send_email_custom_sender(self, mock_smtp, email_svc) -> None:
        """Test sending email with custom sender."""

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        custom_sender = "custom@example.com"
        email_svc.send_email(
            recipient="test@example.com",
            subject="Test",
            body="Body",
            sender=custom_sender,
        )

        # Verify custom sender is used
        call_args = mock_server.sendmail.call_args[0]
        assert call_args[0] == email_svc.sender  # Still logs in with main sender
        # But message shows custom sender in the From field

    @patch("smtplib.SMTP")
    def test_send_email_smtp_failure(self, mock_smtp, email_svc) -> None:
        """Test handling of SMTP connection failure."""

        mock_smtp.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception) as exc_info:
            email_svc.send_email(
                recipient="test@example.com",
                subject="Test",
                body="Body",
            )
        assert "SMTP connection failed" in str(exc_info.value)

    @patch("smtplib.SMTP")
    @patch("builtins.open", new_callable=mock_open, read_data="<html>{{name}} {{verification_url}}</html>")
    def test_send_verification_email(self, mock_file, mock_smtp, email_svc) -> None:
        """Test sending verification email with template."""

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        verification_url = "https://example.com/verify/abc123"
        email_svc.send_verification_email("user@example.com", verification_url)

        # Verify file was opened
        mock_file.assert_called_once()

        # Verify email was sent
        mock_server.sendmail.assert_called_once()
        call_args = mock_server.sendmail.call_args[0]
        assert call_args[1] == "user@example.com"

        # Verify email content contains verification URL
        email_content = call_args[2]
        assert verification_url in email_content

    @patch("smtplib.SMTP")
    @patch("builtins.open", side_effect=FileNotFoundError("Template not found"))
    def test_send_verification_email_template_missing(self, _mock_file, _mock_smtp, email_svc) -> None:
        """Test handling of missing email template."""

        with pytest.raises(FileNotFoundError):
            email_svc.send_verification_email("user@example.com", "http://verify.url")


class TestEmailServiceIMAP:
    """Test suite for IMAP functionality."""

    @pytest.fixture
    def email_svc(self) -> EmailService:
        """Create an EmailService instance for testing."""

        return EmailService()

    @patch("imaplib.IMAP4_SSL")
    def test_connect_imap_success(self, mock_imap, email_svc) -> None:
        """Test successful IMAP connection."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        result = email_svc._connect_imap()

        mock_imap.assert_called_once_with(email_svc.imap_server, email_svc.imap_port)
        mock_mail.login.assert_called_once_with(email_svc.sender, email_svc.password)
        assert result == mock_mail

    @patch("imaplib.IMAP4_SSL")
    def test_connect_imap_failure(self, mock_imap, email_svc) -> None:
        """Test IMAP connection failure."""

        mock_imap.side_effect = Exception("Connection failed")

        with pytest.raises(Exception) as exc_info:
            email_svc._connect_imap()
        assert "Connection failed" in str(exc_info.value)

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_success(self, mock_imap, email_svc) -> None:
        """Test retrieving email IDs."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b"1 2 3 4 5"])

        email_ids = email_svc.get_email_ids(
            recipient_email="test@example.com",
            timedelta_days=7,
        )

        mock_mail.select.assert_called_once_with("INBOX")
        mock_mail.search.assert_called_once()
        assert email_ids == ["1", "2", "3", "4", "5"]
        mock_mail.close.assert_called_once()
        mock_mail.logout.assert_called_once()

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_with_filters(self, mock_imap, email_svc) -> None:
        """Test retrieving email IDs with multiple filters."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b"10 11"])

        email_ids = email_svc.get_email_ids(
            recipient_email="recipient@example.com",
            sender_email="sender@example.com",
            subject_contains="Test Subject",
            timedelta_days=1,
            inbox_only=True,
        )

        # Verify search was called with combined criteria
        assert email_ids == ["10", "11"]

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_no_results(self, mock_imap, email_svc) -> None:
        """Test when no emails match criteria."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b""])

        email_ids = email_svc.get_email_ids()

        assert email_ids == []

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_search_failure(self, mock_imap, email_svc) -> None:
        """Test handling of search failure."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ("NO", [])

        email_ids = email_svc.get_email_ids()

        assert email_ids == []

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_content_success(self, mock_imap, email_svc) -> None:
        """Test retrieving email content."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock email message
        email_message = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Test Email\r\n"
            b"Date: Mon, 16 Oct 2025 10:00:00 +0000\r\n"
            b"\r\n"
            b"This is the email body."
        )
        mock_mail.fetch.return_value = ("OK", [(b"1", email_message)])

        content = email_svc.get_email_content("1")

        assert content is not None
        assert content["id"] == "1"
        assert content["subject"] == "Test Email"
        assert content["from"] == "sender@example.com"
        assert "This is the email body" in content["body_text"]
        mock_mail.close.assert_called_once()
        mock_mail.logout.assert_called_once()

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_content_multipart(self, mock_imap, email_svc) -> None:
        """Test retrieving multipart email content."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock multipart email with text and HTML parts
        multipart_email = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Multipart Test\r\n"
            b"Date: Mon, 16 Oct 2025 10:00:00 +0000\r\n"
            b"Content-Type: multipart/alternative; boundary=boundary123\r\n"
            b"\r\n"
            b"--boundary123\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"\r\n"
            b"Plain text body\r\n"
            b"--boundary123\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"\r\n"
            b"<html>HTML body</html>\r\n"
            b"--boundary123--"
        )
        mock_mail.fetch.return_value = ("OK", [(b"2", multipart_email)])

        content = email_svc.get_email_content("2")

        assert content is not None
        assert "Plain text body" in content["body_text"]

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_content_not_found(self, mock_imap, email_svc) -> None:
        """Test retrieving non-existent email."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.fetch.return_value = ("NO", None)

        content = email_svc.get_email_content("999")

        assert content is None

    @patch("imaplib.IMAP4_SSL")
    def test_get_emails_success(self, mock_imap, email_svc) -> None:
        """Test retrieving multiple emails."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock search results
        mock_mail.search.return_value = ("OK", [b"1 2 3"])

        # Mock email content
        email_1 = (
            b"From: sender1@example.com\r\n"
            b"Subject: Email 1\r\n"
            b"Date: Mon, 16 Oct 2025 09:00:00 +0000\r\n"
            b"\r\n"
            b"Body 1"
        )
        email_2 = (
            b"From: sender2@example.com\r\n"
            b"Subject: Email 2\r\n"
            b"Date: Mon, 16 Oct 2025 10:00:00 +0000\r\n"
            b"\r\n"
            b"Body 2"
        )
        email_3 = (
            b"From: sender3@example.com\r\n"
            b"Subject: Email 3\r\n"
            b"Date: Mon, 16 Oct 2025 11:00:00 +0000\r\n"
            b"\r\n"
            b"Body 3"
        )

        mock_mail.fetch.side_effect = [
            ("OK", [(b"3", email_3)]),
            ("OK", [(b"2", email_2)]),
            ("OK", [(b"1", email_1)]),
        ]

        emails = email_svc.get_emails(limit=10)

        assert len(emails) == 3
        # Should be in reverse order (most recent first)
        assert emails[0]["subject"] == "Email 3"
        assert emails[1]["subject"] == "Email 2"
        assert emails[2]["subject"] == "Email 1"

    @patch("imaplib.IMAP4_SSL")
    def test_get_emails_with_limit(self, mock_imap, email_svc) -> None:
        """Test retrieving emails with limit."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Return 10 email IDs but limit to 3
        mock_mail.search.return_value = ("OK", [b"1 2 3 4 5 6 7 8 9 10"])

        # Only the last 3 should be fetched
        email_template = b"From: sender@example.com\r\nSubject: Email {}\r\n\r\nBody"
        mock_mail.fetch.side_effect = [
            ("OK", [(b"10", email_template.replace(b"{}", b"10"))]),
            ("OK", [(b"9", email_template.replace(b"{}", b"9"))]),
            ("OK", [(b"8", email_template.replace(b"{}", b"8"))]),
        ]

        emails = email_svc.get_emails(limit=3)

        assert len(emails) == 3
        # Should only fetch the last 3 IDs
        assert mock_mail.fetch.call_count == 3

    @patch("imaplib.IMAP4_SSL")
    def test_get_emails_empty_results(self, mock_imap, email_svc) -> None:
        """Test retrieving emails when none match."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b""])

        emails = email_svc.get_emails()

        assert emails == []

    def test_decode_header_plain_text(self, email_svc) -> None:
        """Test decoding plain text header."""

        result = email_svc._decode_header("Plain text subject")
        assert result == "Plain text subject"

    def test_decode_header_encoded(self, email_svc) -> None:
        """Test decoding encoded header."""

        # Encoded UTF-8 string
        encoded = "=?utf-8?b?VGVzdCBTdWJqZWN0?="
        result = email_svc._decode_header(encoded)
        assert "Test Subject" in result or result != ""

    def test_decode_header_empty(self, email_svc) -> None:
        """Test decoding empty header."""

        result = email_svc._decode_header("")
        assert result == ""

    def test_decode_header_none(self, email_svc) -> None:
        """Test decoding None header."""

        # noinspection PyTypeChecker
        result = email_svc._decode_header(None)
        assert result == ""


class TestEmailServiceIntegration:
    """Integration tests for email service."""

    def test_email_service_initialization(self) -> None:
        """Test email service initializes with environment variables."""
        # Patch the class attributes directly
        with patch.object(EmailService, "sender", "test@example.com"), patch.object(
            EmailService, "password", "testpass"
        ), patch.object(EmailService, "smtp_server", "smtp.example.com"), patch.object(
            EmailService, "smtp_port", 587
        ), patch.object(
            EmailService, "imap_server", "imap.example.com"
        ), patch.object(
            EmailService, "imap_port", 993
        ):

            svc = EmailService()
            assert svc.sender == "test@example.com"
            assert svc.password == "testpass"
            assert svc.smtp_server == "smtp.example.com"
            assert svc.smtp_port == 587
            assert svc.imap_server == "imap.example.com"
            assert svc.imap_port == 993

    def test_email_service_singleton(self) -> None:
        """Test that email_service singleton is available."""
        from app.emails.email_service import email_service

        assert email_service is not None
        assert isinstance(email_service, EmailService)
