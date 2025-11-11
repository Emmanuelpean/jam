"""Module for sending and reading emails using SMTP and IMAP."""

import email
import imaplib

# import os
import smtplib
from datetime import datetime, timedelta
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import settings
from app.emails.utils import clean_email_address
from app.utils import AppLogger

templates = Jinja2Templates(directory="templates")


# def open_file(filepath: str) -> str:
#     """Helper function to open a text file from the resources directory.
#     :param filepath: The name of the file located in the resources directory"""
#
#     base_dir = os.path.dirname(__file__)
#     filepath = os.path.join(base_dir, "..\\..\\", "tests/resources", filepath)
#     with open(filepath, "r") as ofile:
#         return ofile.read()
#

# def get_test_emails() -> dict:
#     """Helper function to get test emails from the resources directory."""
#
#     if settings.test_mode:
#         from tests.utils.table_data import USER_DATA
#
#         return {
#             "1": {
#                 "sender": USER_DATA[0]["email"],
#                 "content": open_file("indeed_email.txt"),
#                 "subject": "Indeed 1",
#                 "from": "alert@indeed.com",
#                 "platform": "indeed",
#             },
#             "2": {
#                 "sender": USER_DATA[0]["email"],
#                 "content": open_file("linkedin_email.txt"),
#                 "subject": "Linkedin 1",
#                 "from": "jobalerts-noreply@linkedin.com",
#                 "platform": "linkedin",
#             },
#             "5": {
#                 "sender": USER_DATA[0]["email"],
#                 "content": open_file("indeed_email_2.txt"),
#                 "subject": "Indeed 2",
#                 "from": "alert@indeed.com",
#                 "platform": "indeed",
#             },
#             "6": {
#                 "sender": USER_DATA[0]["email"],
#                 "content": open_file("linkedin_email_2.txt"),
#                 "subject": "Linkedin 2",
#                 "from": "jobalerts-noreply@linkedin.com",
#                 "platform": "linkedin",
#             },
#             "7": {
#                 "sender": USER_DATA[0]["email"],
#                 "content": open_file("veganjobs_email_1.txt"),
#                 "subject": "VeganJobs 1",
#                 "from": "info@veganjobs.com",
#                 "platform": "veganjobs",
#             },
#             "3": {
#                 "sender": USER_DATA[3]["email"],
#                 "content": open_file("indeed_email.txt"),
#                 "subject": "Indeed 2",
#                 "from": "alert@indeed.com",
#                 "platform": "indeed",
#             },
#             "4": {
#                 "sender": USER_DATA[3]["email"],
#                 "content": open_file("linkedin_email.txt"),
#                 "subject": "Linkedin 2",
#                 "from": "jobalerts-noreply@linkedin.com",
#                 "platform": "linkedin",
#             },
#         }
#     else:
#         return {}


class EmailService(object):
    """Email service class for sending and reading emails."""

    sender = settings.email_username
    password = settings.email_password
    smtp_server = settings.email_smtp_host
    smtp_port = settings.email_smtp_port
    imap_server = settings.email_imap_host
    imap_port = settings.email_imap_port

    def __init__(self) -> None:
        """Initialize the EmailService class."""

        self.logger = AppLogger.create_service_logger("EmailService", "INFO")
        self.test_emails = []

        # Setup Jinja2 templates using FastAPI's built-in class
        current_dir = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(current_dir / "templates"))

    @property
    def current_datetime(self) -> str:
        """Get the current date and time formatted as a string."""

        return datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        sender: str | None = None,
        message_type: str = "",
    ) -> None:
        """Send an email to the specified recipient.
        :param recipient: The recipient's email address.
        :param subject: The subject of the email.
        :param body: The body of the email in HTML format.
        :param message_type: The type of email being sent (for logging purposes).
        :param sender: The sender's email address (optional, defaults to configured sender)."""

        if settings.test_mode:
            self.test_emails.append(
                {
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                    "sender": sender or self.sender,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = settings.email_username if sender is None else sender
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(settings.email_smtp_host, settings.email_smtp_port) as server:
                server.starttls()
                server.login(settings.email_username, settings.email_password)
                server.sendmail(settings.email_username, recipient, msg.as_string())
            self.logger.info(f"{message_type} email sent to %s with subject: %s", recipient, subject)
        except Exception as e:
            self.logger.error(f"Failed to send {message_type} email to %s: %s", recipient, str(e))
            raise e

    def send_verification_email(
        self,
        recipient: str,
        verification_url: str,
    ) -> None:
        """Send a verification email to the specified recipient.
        :param recipient: The recipient's email address.
        :param verification_url: The email verification URL."""

        template = self.templates.env.get_template("email_confirmation.html")
        html_content = template.render(
            name="there",
            confirmation_url=verification_url,
            token_expiry_min=settings.verification_token_expiration_minutes,
        )

        self.send_email(
            recipient,
            "Please verify your email",
            html_content,
            settings.support_email,
            "Email verification",
        )

    def send_email_change_verification(
        self,
        recipient: str,
        verification_url: str,
    ) -> None:
        """Send an email change verification email to the specified recipient.
        :param recipient: The recipient's email address.
        :param verification_url: The email change verification URL."""

        template = self.templates.env.get_template("email_change.html")
        html_content = template.render(
            name="there",
            confirmation_url=verification_url,
            token_expiry_min=settings.verification_token_expiration_minutes,
        )

        self.send_email(
            recipient,
            "Please verify your email",
            html_content,
            settings.support_email,
            "Email change verification",
        )

    def send_password_reset_email(
        self,
        recipient: str,
        reset_url: str,
    ) -> None:
        """Send a password reset email to the specified recipient.
        :param recipient: The recipient's email address.
        :param reset_url: The password reset URL."""

        template = self.templates.env.get_template("password_reset.html")
        html_content = template.render(
            reset_url=reset_url, token_expiry_min=settings.verification_token_expiration_minutes
        )

        self.send_email(
            recipient,
            "Reset your password",
            html_content,
            settings.support_email,
            "Password Reset",
        )

    def send_password_changed_notification(
        self,
        recipient: str,
    ) -> None:
        """Send an email to the specified recipient mentioning that the password was changed.
        :param recipient: The recipient's email address."""

        template = self.templates.env.get_template("password_changed.html")
        html_content = template.render(change_date=self.current_datetime, support_email=settings.support_email)

        subject = "Your JAM Password Has Been Changed"
        self.send_email(
            recipient,
            subject,
            html_content,
            settings.support_email,
            "Password changed notification",
        )

    def send_email_change_notification(
        self,
        recipient: str,
    ) -> None:
        """Send an email to the specified recipient mentioning that the email was changed.
        :param recipient: The recipient's email address."""

        template = self.templates.env.get_template("email_changed.html")
        html_content = template.render(change_date=self.current_datetime, support_email=settings.support_email)

        subject = "Your JAM Email Address Has Been Changed"
        self.send_email(
            recipient,
            subject,
            html_content,
            settings.support_email,
            "Email change notification",
        )

    @staticmethod
    def _connect_imap() -> imaplib.IMAP4_SSL:
        """Connect to IMAP server and login.
        :return: IMAP connection object"""

        mail = imaplib.IMAP4_SSL(settings.email_imap_host, settings.email_imap_port)
        mail.login(settings.email_username, settings.email_password)
        return mail

    def get_test_emails(self, recipient: str = None) -> list[dict]:
        """Get test emails for a specific recipient or all test emails."""

        if not settings.test_mode:
            raise ValueError("Test mode is not enabled")

        if recipient:
            return [e for e in self.test_emails if e["recipient"] == recipient]
        return self.test_emails

    def clear_test_emails(self) -> None:
        """Clear all stored test emails."""

        if settings.test_mode:
            self.test_emails = []

    def get_email_ids(
        self,
        recipient_email: str = "",
        sender_email: str = "",
        inbox_only: bool = True,
        timedelta_days: int | float = 1,
        subject_contains: str = "",
    ) -> list[str]:
        """Search for messages matching a query.
        :param recipient_email: Filter by recipient email address (e.g. jam.jobscraper@emmanuelpean.me)
        :param sender_email: Filter by sender email address (e.g. emmanuelpean@gmail.com)
        :param inbox_only: Search only in the inbox (True) or all folders (False)
        :param timedelta_days: Number of days to search for emails
        :param subject_contains: Filter by subject content
        :return: List of message IDs matching the query"""

        # # Test mode
        # if settings.test_mode:
        #     TEST_EMAILS = get_test_emails()
        #     return [key for key in TEST_EMAILS if TEST_EMAILS[key]["sender"] == sender_email]

        mail = self._connect_imap()

        try:
            # Select mailbox
            mailbox = "INBOX" if inbox_only else "ALL"
            mail.select(mailbox)

            # Build IMAP search criteria
            search_criteria = []

            # Date filter
            if timedelta_days:
                since_date = (datetime.now() - timedelta(days=timedelta_days)).strftime("%d-%b-%Y")
                search_criteria.append(f"SINCE {since_date}")

            if recipient_email:
                search_criteria.append(f'HEADER X-Forwarded-To "{recipient_email}"')

            # Sender filter
            if sender_email:
                search_criteria.append(f'HEADER Delivered-To "{sender_email}"')

            # Subject filter
            if subject_contains:
                search_criteria.append(f'SUBJECT "{subject_contains}"')

            # Default to all if no criteria
            search_query = " ".join(search_criteria) if search_criteria else "ALL"

            # Execute search
            status, message_ids = mail.search(None, search_query)

            if status != "OK":
                return []

            # Parse message IDs
            email_ids = message_ids[0].split()
            return [msg_id.decode() for msg_id in email_ids]

        finally:
            mail.close()
            mail.logout()

    def get_email_data(
        self,
        email_id: str,
    ) -> dict[str, str | datetime] | None:
        """Get the content of a specific email by ID.
        :param email_id: The email message ID
        :return: Dictionary with email details (subject, from, date, body)"""

        # if settings.test_mode:
        #     TEST_EMAILS = get_test_emails()
        #     email_data = TEST_EMAILS[email_id]
        #     return {
        #         "id": email_id,
        #         "subject": email_data["subject"],
        #         "from": email_data["from"],
        #         "date": datetime.now(),
        #         "body": email_data["content"],
        #     }

        mail = self._connect_imap()

        try:
            mail.select("INBOX")

            # Fetch the email
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                return None

            # Parse email content
            # noinspection PyUnresolvedReferences
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract headers
            subject = self._decode_header(msg["Subject"])
            from_email = clean_email_address(self._decode_header(msg["From"]))
            to_email = clean_email_address(self._decode_header(msg["To"]))

            # Extract date
            date = msg["Date"]
            date_formats = [
                "%a, %d %b %Y %H:%M:%S %z",  # Standard RFC 2822: "Thu, 14 Aug 2025 02:25:53 +0000"
                "%a, %d %b %Y %H:%M:%S %z (UTC)",  # Original format with (UTC)
                "%a, %d %b %Y %H:%M:%S",  # Without timezone
                "%d %b %Y %H:%M:%S %z",  # Without day name
                "%a, %d %b %Y %H:%M:%S GMT",  # GMT timezone
                "%a, %d %b %Y %H:%M:%S UTC",  # UTC timezone
            ]

            date_received = None
            for date_format in date_formats:
                try:
                    date_received = datetime.strptime(date, date_format)
                    break
                except ValueError:
                    continue

            # Extract body
            body_text = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue

                    # Get email body
                    if content_type == "text/plain":
                        body_text = part.get_payload(decode=True).decode()

            else:
                # Not multipart - simple email
                body_text = msg.get_payload(decode=True).decode()

            return {
                "id": email_id,
                "subject": subject,
                "from": from_email,
                "to": to_email,
                "date": date_received,
                "body": body_text,
            }

        finally:
            mail.close()
            mail.logout()

    def get_emails(self, *args, **kwargs) -> list[dict[str, str]]:
        """Get multiple emails matching criteria.
        :param args: arguments passed to get_email_ids
        :param kwargs: Keyword arguments passed to get_email_ids
        :return: List of email content dictionaries"""

        email_ids = self.get_email_ids(*args, **kwargs)
        emails = []
        for email_id in reversed(email_ids):  # Most recent first
            content = self.get_email_data(email_id)
            if content:
                emails.append(content)

        return emails

    @staticmethod
    def _decode_header(header: str) -> str:
        """Decode email header.
        :param header: Raw header string
        :return: Decoded header string"""

        if not header:
            return ""

        decoded_parts = decode_header(header)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or "utf-8")
            else:
                decoded_string += part

        return decoded_string

    def delete_email(
        self,
        email_id: str,
    ) -> bool:
        """Delete an email by ID from the inbox.
        :param email_id: The email message ID to delete
        :return: True if deletion successful, False otherwise"""

        if settings.test_mode:
            return True

        mail = self._connect_imap()

        try:
            mail.select("INBOX")

            # Mark the email as deleted
            status, _ = mail.store(email_id, "+FLAGS", "\\Deleted")

            if status != "OK":
                return False

            # Permanently remove emails marked as deleted
            mail.expunge()

            return True

        finally:
            mail.close()
            mail.logout()


email_service = EmailService()
# # # # send_email = email_service.send_email("emmanuel.pean@gmail.com", "test", "test body", "jam.info@emmanuelpean.me")
# # #
# Get multiple emails at once
# emails = email_service.get_emails(
#     timedelta_days=1,
#     recipient_email="jam.jobscraper@emmanuelpean.me",
#     inbox_only=True,
#     sender_email="emmanuelpean@gmail.com",
#     # subject_contains="Job Alert Results",
# )
# for email in emails:
#     print(email["body"], "\n\n")
