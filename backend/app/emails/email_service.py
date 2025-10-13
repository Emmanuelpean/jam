"""Module for sending and reading emails using SMTP and IMAP."""

import os
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class EmailService(object):
    """Email service class for sending and reading emails."""

    sender = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("EMAIL_SMTP_HOST")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT"))
    imap_server = os.getenv("EMAIL_IMAP_HOST")
    imap_port = int(os.getenv("EMAIL_IMAP_PORT"))

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
        msg["From"] = self.sender if sender is None else sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, recipient, msg.as_string())

    async def send_verification_email(
        self,
        recipient: str,
        verification_url: str,
    ) -> None:
        """Send a verification email to the specified recipient.
        :param recipient: The recipient's email address.
        :param verification_url: The verification URL."""

        with open("email_template.html", "r") as file:
            html_template = file.read()
        html_content = html_template.replace("{{name}}", "there")
        html_content = html_content.replace("{{verification_url}}", verification_url)

        self.send_email(recipient, "Please verify your email", html_content)

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server and login.
        :return: IMAP connection object"""

        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.sender, self.password)
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
