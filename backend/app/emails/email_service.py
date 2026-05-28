"""Module for sending and reading emails using SMTP and IMAP."""

import email
import imaplib
import smtplib
from datetime import datetime, timedelta
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.emails.routers.templates import email_templates
from app.emails.utils import clean_email_address, build_multi_from_query
from app.utils import AppLogger


class EmailService(object):
    """Email service class for sending and reading emails."""

    smtp_server = settings.email_smtp_host
    smtp_port = settings.email_smtp_port
    imap_server = settings.email_imap_host
    imap_port = settings.email_imap_port

    def __init__(self, email_username: str, email_password: str) -> None:
        """Initialise the EmailService class
        :param email_username: The email username for SMTP/IMAP authentication.
        :param email_password: The email password for SMTP/IMAP authentication."""

        self.email_username = email_username
        self.email_password = email_password
        self.logger = AppLogger.create_service_logger("email_service", "INFO")
        self.test_emails = []
        self.templates = email_templates

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
        :param sender: The sender's email address alias (optional, defaults to configured sender)."""

        if settings.test_mode:
            self.test_emails.append(
                {
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                    "sender": sender or self.email_username,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_username if sender is None else sender
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.sendmail(self.email_username, recipient, msg.as_string())
                self.logger.info(f"{message_type} email sent to %s with subject: %s", recipient, subject)
        except Exception as e:
            self.logger.error(f"Failed to send {message_type} email to %s: %s", recipient, str(e))
            raise e

    def send_verification_email(
        self,
        recipient: str,
        verification_url: str,
        recipient_name: str | None = None,
    ) -> None:
        """Send a verification email to the specified recipient.
        :param recipient: The recipient's email address.
        :param verification_url: The email verification URL.
        :param recipient_name: The recipient name."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("email_confirmation.html")
        html_content = template.render(
            name=recipient_name if recipient_name else "there",
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
        recipient_name: str | None = None,
    ) -> None:
        """Send an email change verification email to the specified recipient.
        :param recipient: The recipient's email address.
        :param verification_url: The email change verification URL.
        :param recipient_name: The recipient name."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("email_change.html")
        html_content = template.render(
            name=recipient_name if recipient_name else "there",
            confirmation_url=verification_url,
            token_expiry_min=settings.email_change_token_expiration_minutes,
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
        recipient_name: str | None = None,
    ) -> None:
        """Send a password reset email to the specified recipient.
        :param recipient: The recipient's email address.
        :param reset_url: The password reset URL.
        :param recipient_name: The recipient name."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("password_reset.html")
        html_content = template.render(
            name=recipient_name if recipient_name else "there",
            reset_url=reset_url,
            token_expiry_min=settings.password_reset_token_expiration_minutes,
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

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
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
        old_email: str,
    ) -> None:
        """Send an email to the specified recipient mentioning that the email was changed.
        :param recipient: The recipient's email address.
        :param old_email: The old email address before the change."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("email_changed.html")
        html_content = template.render(
            change_date=self.current_datetime,
            support_email=settings.support_email,
            old_email=old_email,
            new_email=recipient,
        )

        subject = "Your JAM Email Address Has Been Changed"
        self.send_email(
            recipient,
            subject,
            html_content,
            settings.support_email,
            "Email change notification",
        )

    def send_trial_end_notification(
        self,
        recipient: str,
        end_date: datetime,
    ) -> None:
        """Send an email to the specified recipient mentioning that the email was changed.
        :param recipient: The recipient's email address.
        :param end_date: The trial end date."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("trial_end_reminder.html")
        html_content = template.render(
            upgrade_url=settings.frontend_url + "/settings/premium",
            end_date=end_date.strftime("%B %d, %Y"),
            support_email=settings.support_email,
        )

        subject = "Your TOAST Free Trial is Ending Soon"
        self.send_email(
            recipient,
            subject,
            html_content,
            settings.support_email,
            "Trial end notification",
        )

    def send_new_version_email(
        self,
        recipient: str,
        version: str,
        features: list[dict],
    ) -> None:
        """Send a new version announcement email to the specified recipient.
        :param recipient: The recipient's email address.
        :param version: The version string (e.g. "1.2.0").
        :param features: List of feature dicts with title, description, and optional image_url."""

        if not self.templates.env:
            raise AssertionError("Jinja2 environment not initialised")
        template = self.templates.env.get_template("new_version.html")
        html_content = template.render(
            version=version,
            features=features,
            app_url=settings.frontend_url,
        )

        self.send_email(
            recipient,
            f"JAM v{version} is Here! \u2014 See What's New",
            html_content,
            settings.info_email,
            "New version announcement",
        )

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server and login.
        :return: IMAP connection object"""

        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email_username, self.email_password)
        return mail

    def get_test_emails(self, recipient: str | None = None) -> list[dict]:
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
        inbox: str = "INBOX",
        timedelta_days: int | float = 1,
        subject_contains: str = "",
        from_email: list[str] | str = "",
        to_email: str = "",
    ) -> list[str]:
        """Search for messages matching a query.
        :param recipient_email: Filter by recipient email address (e.g. jam.jobscraper@emmanuelpean.me)
        :param sender_email: Filter by sender email address (e.g. emmanuelpean@gmail.com)
        :param inbox: Mailbox to search in (default is INBOX)
        :param timedelta_days: Number of days to search for emails
        :param subject_contains: Filter by subject content
        :param from_email: Filter by 'From' email address
        :param to_email: Filter by 'To' email address
        :return: List of message IDs matching the query"""

        mail = self._connect_imap()

        try:
            # Select mailbox
            mail.select(inbox)

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

            # From email filter
            if from_email:
                search_criteria.append(build_multi_from_query(from_email))

            # To email filter
            if to_email:
                search_criteria.append(f'HEADER To "{to_email}"')

            # Default to all if no criteria
            search_query = " ".join(search_criteria) if search_criteria else "ALL"

            # Execute search using UID instead of sequence numbers
            # noinspection PyTypeChecker
            status, message_ids = mail.uid("search", None, search_query)

            if status != "OK":
                return []

            # Parse message UIDs (more stable than sequence numbers)
            email_ids = message_ids[0].split()
            return [msg_id.decode() for msg_id in email_ids]

        finally:
            mail.close()
            mail.logout()

    def get_email_data(self, email_id: str) -> dict[str, str | None | datetime] | None:
        """Get the content of a specific email by ID.
        :param email_id: The email message UID (unique identifier)
        :return: Dictionary with email details (subject, from, date, body)"""

        mail = self._connect_imap()

        try:
            mail.select("INBOX")

            # Fetch the email using UID
            status, msg_data = mail.uid("fetch", email_id, "(RFC822)")

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
            message_id = msg.get("Message-ID", "").strip()

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

            body_text = ""
            html_text = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" in content_disposition:
                        continue

                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"

                    if not isinstance(payload, bytes):
                        # multipart container parts return None — skip them
                        continue

                    if content_type == "text/plain":
                        try:
                            body_text = payload.decode(charset)
                        except UnicodeDecodeError:
                            body_text = payload.decode("windows-1252", errors="replace")

                    elif content_type == "text/html":
                        try:
                            html_text = payload.decode(charset)
                        except UnicodeDecodeError:
                            html_text = payload.decode("windows-1252", errors="replace")
            else:
                # single-part message
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True)
                if not isinstance(payload, bytes):
                    raise AssertionError("Payload is not bytes")
                body_text = payload.decode()
                if content_type == "text/html":
                    html_text = body_text

            # Prefer text, but fallback to HTML if needed
            final_body = html_text or body_text

            return {
                "id": email_id,
                "message_id": message_id,
                "subject": subject,
                "from": from_email,
                "to": to_email,
                "date": date_received,
                "body": final_body,
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
    def _decode_header(header: str | None) -> str:
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
        :param email_id: The email message UID to delete
        :return: True if deletion is successful, False otherwise"""

        if settings.test_mode:
            return True

        mail = self._connect_imap()

        try:
            mail.select("INBOX")

            # Mark the email as deleted using UID
            status, _ = mail.uid("store", email_id, "+FLAGS", "\\Deleted")

            if status != "OK":
                return False

            # Permanently remove emails marked as deleted
            mail.expunge()

            return True

        finally:
            mail.close()
            mail.logout()


email_service = EmailService(settings.main_email_username, settings.main_email_password)
