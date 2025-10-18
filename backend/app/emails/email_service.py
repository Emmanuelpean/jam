"""Module for sending and reading emails using SMTP and IMAP."""

import email
import imaplib
import smtplib
from datetime import datetime, timedelta
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Optional

from fastapi.templating import Jinja2Templates

from app.config import settings

templates = Jinja2Templates(directory="templates")


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

        # Setup Jinja2 templates using FastAPI's built-in class
        current_dir = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(current_dir / "templates"))

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        sender: str | None = None,
    ) -> None:
        """Send an email to the specified recipient.
        :param recipient: The recipient's email address.
        :param subject: The subject of the email.
        :param body: The body of the email in HTML format.
        :param sender: The sender's email address (optional, defaults to configured sender)."""

        msg = MIMEMultipart()
        msg["From"] = settings.email_username if sender is None else sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.email_smtp_host, settings.email_smtp_port) as server:
            server.starttls()
            server.login(settings.email_username, settings.email_password)
            server.sendmail(settings.email_username, recipient, msg.as_string())

    def send_verification_email(
        self,
        recipient: str,
        verification_url: str,
    ) -> None:
        """Send a verification email to the specified recipient."""

        template = self.templates.env.get_template("email_confirmation.html")
        html_content = template.render(
            name="there",
            confirmation_url=verification_url,
            token_expiry_min=settings.verification_token_expiration_minutes,
        )

        self.send_email(recipient, "Please verify your email", html_content, settings.support_email)

    def send_password_reset_email(
        self,
        recipient: str,
        reset_url: str,
    ) -> None:
        """Send a password reset email to the specified recipient."""

        template = self.templates.env.get_template("password_reset.html")
        html_content = template.render(
            reset_url=reset_url, token_expiry_min=settings.verification_token_expiration_minutes
        )

        self.send_email(recipient, "Reset your password", html_content, settings.support_email)

    def send_password_changed_notification(
        self,
        recipient: str,
    ) -> None:
        """Send an email to the specified recipient mentioning that the password was changed."""

        change_date = datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")

        template = self.templates.env.get_template("password_changed.html")
        html_content = template.render(change_date=change_date, support_email=settings.support_email)

        subject = "Your JAM Password Has Been Changed"
        self.send_email(recipient, subject, html_content, settings.support_email)

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server and login.
        :return: IMAP connection object"""

        mail = imaplib.IMAP4_SSL(settings.email_imap_host, settings.email_imap_port)
        mail.login(settings.email_username, settings.email_password)
        return mail

    def get_email_ids(
        self,
        recipient_email: str = "",
        sender_email: str = "",
        inbox_only: bool = True,
        timedelta_days: int | float = 1,
        subject_contains: str = "",
    ) -> List[str]:
        """Search for messages matching a query.
        :param recipient_email: Filter by recipient email address (e.g. jam.jobscraper@emmanuelpean.me)
        :param sender_email: Filter by sender email address (e.g. emmanuelpean@gmail.com)
        :param inbox_only: Search only in the inbox (True) or all folders (False)
        :param timedelta_days: Number of days to search for emails
        :param subject_contains: Filter by subject content
        :return: List of message IDs matching the query"""

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

    def get_email_content(
        self,
        email_id: str,
    ) -> Optional[Dict[str, str]]:
        """Get the content of a specific email by ID.
        :param email_id: The email message ID
        :return: Dictionary with email details (subject, from, date, body)"""

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
            from_email = self._decode_header(msg["From"])
            date = msg["Date"]

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
                "date": date,
                "body_text": body_text,
            }

        finally:
            mail.close()
            mail.logout()

    def get_emails(
        self,
        recipient_email: str = "",
        sender_email: str = "",
        inbox_only: bool = True,
        timedelta_days: int | float = 1,
        subject_contains: str = "",
        limit: int = 10,
    ) -> List[Dict[str, str]]:
        """Get multiple emails matching criteria.
        :param recipient_email: Filter by recipient email address
        :param sender_email: Filter by sender email address
        :param inbox_only: Search only in the inbox
        :param timedelta_days: Number of days to search for emails
        :param subject_contains: Filter by subject content
        :param limit: Maximum number of emails to retrieve
        :return: List of email content dictionaries"""

        email_ids = self.get_email_ids(
            recipient_email=recipient_email,
            sender_email=sender_email,
            inbox_only=inbox_only,
            timedelta_days=timedelta_days,
            subject_contains=subject_contains,
        )

        # Limit results
        email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

        emails = []
        for email_id in reversed(email_ids):  # Most recent first
            content = self.get_email_content(email_id)
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


email_service = EmailService()
# # send_email = email_service.send_email("emmanuel.pean@gmail.com", "test", "test body", "jam.info@emmanuelpean.me")
#
# # Get multiple emails at once
# emails = email_service.get_emails(
#     timedelta_days=1,
#     limit=5,
#     recipient_email="jam.jobscraper@emmanuelpean.me",
#     inbox_only=True,
#     sender_email="emmanuelpean@gmail.com",
# )
# for email in emails:
#     print(email)
