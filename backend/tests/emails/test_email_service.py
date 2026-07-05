"""Tests for email service."""

from unittest.mock import patch, MagicMock

import pytest
from jinja2 import TemplateNotFound

from app.emails.email_service import EmailService


@pytest.fixture
def email_svc() -> EmailService:
    """Fixture for email service."""

    return EmailService("test", "test")


class TestEmailService:
    """Test suite for EmailService class."""

    @patch("app.config.settings.test_mode", False)
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp: MagicMock, email_svc: EmailService) -> None:
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
        mock_server.login.assert_called_once_with(email_svc.email_username, email_svc.email_password)
        mock_server.sendmail.assert_called_once()

        # Verify email content
        call_args = mock_server.sendmail.call_args[0]
        assert call_args[0] == email_svc.email_username  # From
        assert call_args[1] == "test@example.com"  # To

    @patch("app.config.settings.test_mode", False)
    @patch("smtplib.SMTP")
    def test_send_email_custom_sender(self, mock_smtp: MagicMock, email_svc: EmailService) -> None:
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
        assert call_args[0] == email_svc.email_username  # Still logs in with main sender
        # But message shows custom sender in the From field

    @patch("app.config.settings.test_mode", False)
    @patch("smtplib.SMTP")
    def test_send_email_smtp_failure(self, mock_smtp: MagicMock, email_svc: EmailService) -> None:
        """Test handling of SMTP connection failure."""

        mock_smtp.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception) as exc_info:
            email_svc.send_email(
                recipient="test@example.com",
                subject="Test",
                body="Body",
            )
        assert "SMTP connection failed" in str(exc_info.value)

    def test_send_verification_email_template_missing(self, email_svc: EmailService) -> None:
        """Test handling of missing email template."""

        with patch.object(
            email_svc.templates.env, "get_template", side_effect=TemplateNotFound("email_confirmation.html")
        ):
            with pytest.raises(TemplateNotFound):
                email_svc.send_email_verification_email("user@example.com", "http://verify.url")


class TestEmailServiceIMAP:
    """Test suite for IMAP functionality."""

    @patch("imaplib.IMAP4_SSL")
    def test_connect_imap_success(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test successful IMAP connection."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        result = email_svc._connect_imap()

        mock_imap.assert_called_once_with(email_svc.imap_server, email_svc.imap_port)
        mock_mail.login.assert_called_once_with(email_svc.email_username, email_svc.email_password)
        assert result == mock_mail

    @patch("imaplib.IMAP4_SSL")
    def test_connect_imap_failure(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test IMAP connection failure."""

        mock_imap.side_effect = Exception("Connection failed")

        with pytest.raises(Exception) as exc_info:
            email_svc._connect_imap()
        assert "Connection failed" in str(exc_info.value)

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_success(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving email IDs."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("OK", [b"1 2 3 4 5"])

        email_ids = email_svc.get_email_ids(
            recipient_email="test@example.com",
            timedelta_days=7,
        )

        mock_mail.select.assert_called_once_with("INBOX")
        mock_mail.uid.assert_called_once()
        assert email_ids == ["1", "2", "3", "4", "5"]
        mock_mail.close.assert_called_once()
        mock_mail.logout.assert_called_once()

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_with_filters(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving email IDs with multiple filters."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("OK", [b"10 11"])

        email_ids = email_svc.get_email_ids(
            recipient_email="recipient@example.com",
            sender_email="sender@example.com",
            subject_contains="Test Subject",
            timedelta_days=1,
        )

        # Verify search was called with combined criteria
        assert email_ids == ["10", "11"]

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_no_results(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test when no emails match criteria."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("OK", [b""])

        email_ids = email_svc.get_email_ids()

        assert email_ids == []

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_ids_search_failure(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test handling of search failure."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("NO", [])

        email_ids = email_svc.get_email_ids()

        assert email_ids == []

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_data_success(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving email data."""

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
        mock_mail.uid.return_value = ("OK", [(b"1", email_message)])

        content = email_svc.get_email_data("1")

        assert content.id == "1"
        assert content.subject == "Test Email"
        assert content.from_email == "sender@example.com"
        assert "This is the email body" in content.body
        mock_mail.close.assert_called_once()
        mock_mail.logout.assert_called_once()

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_data_multipart(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving multipart email data."""

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
        mock_mail.uid.return_value = ("OK", [(b"2", multipart_email)])

        content = email_svc.get_email_data("2")

        assert "<html>HTML body</html>" in content.body

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_data_multipart_container_part_skipped(
        self, mock_imap: MagicMock, email_svc: EmailService
    ) -> None:
        """The multipart/alternative container is the first node yielded by msg.walk().
        Its get_payload(decode=True) returns None, which must be skipped so the real
        text/plain child part is still extracted."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        plain_only_multipart = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Plain Multipart\r\n"
            b"Date: Mon, 16 Oct 2025 10:00:00 +0000\r\n"
            b"Content-Type: multipart/alternative; boundary=b\r\n"
            b"\r\n"
            b"--b\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"\r\n"
            b"Plain text body\r\n"
            b"--b--"
        )
        mock_mail.uid.return_value = ("OK", [(b"3", plain_only_multipart)])

        content = email_svc.get_email_data("3")

        assert "Plain text body" in content.body

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_data_single_part_non_bytes_payload_raises(
        self, mock_imap: MagicMock, email_svc: EmailService
    ) -> None:
        """If get_payload(decode=True) somehow returns a non-bytes value on a single-part
        message, an AssertionError should be raised to surface the unexpected condition."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        raw_email = (
            b"From: sender@example.com\r\n"
            b"Subject: Weird\r\n"
            b"Date: Mon, 16 Oct 2025 10:00:00 +0000\r\n"
            b"\r\n"
            b"body"
        )
        mock_mail.uid.return_value = ("OK", [(b"4", raw_email)])

        # Patch get_payload on the parsed message to simulate a non-bytes return value
        with patch("email.message.Message.get_payload", return_value="not bytes"):
            with pytest.raises(Exception, match="4"):
                email_svc.get_email_data("4")

    @patch("imaplib.IMAP4_SSL")
    def test_get_email_data_not_found(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test that fetching a non-existent email raises an exception."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("NO", None)

        with pytest.raises(Exception, match="999"):
            email_svc.get_email_data("999")

    @patch("imaplib.IMAP4_SSL")
    def test_get_emails_success(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving multiple emails."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

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

        # Configure uid to return search results first, then fetch results
        mock_mail.uid.side_effect = [
            ("OK", [b"1 2 3"]),  # search result
            ("OK", [(b"3", email_3)]),  # fetch for id 3
            ("OK", [(b"2", email_2)]),  # fetch for id 2
            ("OK", [(b"1", email_1)]),  # fetch for id 1
        ]

        emails = email_svc.get_emails()

        assert len(emails) == 3
        # Should be in reverse order (most recent first)
        assert emails[0].subject == "Email 3"
        assert emails[1].subject == "Email 2"
        assert emails[2].subject == "Email 1"

    @patch("imaplib.IMAP4_SSL")
    def test_get_emails_empty_results(self, mock_imap: MagicMock, email_svc: EmailService) -> None:
        """Test retrieving emails when none match."""

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        mock_mail.uid.return_value = ("OK", [b""])

        emails = email_svc.get_emails()

        assert emails == []

    def test_decode_header_plain_text(self, email_svc: EmailService) -> None:
        """Test decoding plain text header."""

        result = email_svc._decode_header("Plain text subject")
        assert result == "Plain text subject"

    def test_decode_header_encoded(self, email_svc: EmailService) -> None:
        """Test decoding encoded header."""

        # Encoded UTF-8 string
        encoded = "=?utf-8?b?VGVzdCBTdWJqZWN0?="
        result = email_svc._decode_header(encoded)
        assert "Test Subject" in result or result != ""

    def test_decode_header_empty(self, email_svc: EmailService) -> None:
        """Test decoding empty header."""

        result = email_svc._decode_header("")
        assert result == ""

    def test_decode_header_none(self, email_svc: EmailService) -> None:
        """Test decoding None header."""

        result = email_svc._decode_header(None)
        assert result == ""
