"""Gmail Email Retrieval and LinkedIn Job Extraction Module

This module provides functionality to authenticate with Gmail using OAuth 2.0,
retrieve email messages, and extract LinkedIn job IDs from email content.
It offers a complete workflow for accessing Gmail data and parsing job-related
information from email bodies."""

import base64
import json
import os
import pickle
import re
from datetime import datetime
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.database import get_db, SessionLocal
from app.eis.models import JobEmails, JobEmailJobs
from app.models import User
from app.utils import get_gmail_logger, AppLogger

logger = get_gmail_logger()


def extract_email_address(sender_field: str) -> str:
    """Extract a clean email address from the sender field
    Handles formats like:
    - 'John Doe <john.doe@gmail.com>'
    - 'john.doe@gmail.com'
    - '"John Doe" <john.doe@gmail.com>'"""

    name, email = parseaddr(sender_field)
    return email.lower().strip() if email else sender_field.lower().strip()


def get_user_id(email: str, session) -> None | int:
    """Get user id from email"""

    entry = session.query(User).filter(User.email == email).first()
    if entry:
        return entry.id
    else:
        return 1


class GmailScraper(object):
    """Gmail Scrapper"""

    def __init__(
        self,
        token_file: str = "token.pickle",
        secrets_file: str = "eis_secrets.json",
    ) -> None:
        """Object constructor
        :param token_file: Path to the token pickle file
        :param secrets_file: Path to the secrets JSON file containing OAuth credentials"""

        self.token_file = token_file
        self.secrets_file = secrets_file
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.service = None

        # Load credentials from the external file and authenticate
        self.credentials_config = self._load_credentials()
        self.authenticate()

    def _load_credentials(self) -> dict:
        """Load OAuth credentials from the secrets file"""

        try:
            with open(self.secrets_file, "r") as f:
                secrets = json.load(f)
                return secrets["google_auth"]
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Secrets file '{self.secrets_file}' not found. Please create it with your OAuth credentials."
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(
                f"Invalid JSON format in secrets file '{self.secrets_file}' or missing 'google_auth' section: {e}"
            )

    def authenticate(self) -> None:
        """Authenticate and create the Gmail service"""

        credentials: Credentials | None = None

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                credentials = pickle.load(token)

        # If there are no valid credentials, request authorization
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(self.credentials_config, self.SCOPES)
                credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, "wb") as token:
                # noinspection PyTypeChecker
                pickle.dump(credentials, token)

        self.service = build("gmail", "v1", credentials=credentials)

    def check_connection(self) -> bool:
        """Check if the connection to Gmail inbox is working properly

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to get the user's profile which is a lightweight operation
            self.service.users().getProfile(userId="me").execute()
            logger.info("Successfully connected to Gmail inbox")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail inbox: {str(e)}")
            return False

    # ------------------------------------------------- EMAIL READING -------------------------------------------------

    def search_messages(
        self,
        sender_email: str = "",
        timedelta_days: int | float = 1,
        max_results: int = 10,
    ) -> list[str]:
        """Search for messages matching a query"""

        self.check_connection()

        query = ""
        query += f"from:{sender_email}" if sender_email else ""
        query += f" newer_than:{timedelta_days}d" if timedelta_days else ""
        query = query.strip()

        result = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        print(result)
        messages = result.get("messages", [])
        return [msg["id"] for msg in messages]

    def _extract_body(self, payload: dict) -> str:
        """Extract email body from payload"""

        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"]["data"]
                    body = self._decode_base64(data)
                    break
                elif part["mimeType"] == "text/html":
                    data = part["body"]["data"]
                    body = self._decode_base64(data)
        else:
            if payload["mimeType"] == "text/plain":
                data = payload["body"]["data"]
                body = self._decode_base64(data)

        return body

    @staticmethod
    def _decode_base64(data: str) -> str:
        """Decode base64 URL-safe string"""

        return base64.urlsafe_b64decode(data).decode("utf-8")

    def get_message_data(self, message_id: str) -> dict[str, str] | None:
        """Extract readable content from an email
        :param message_id: Message ID
        :return: Dictionary containing email metadata and body content"""

        message = self.service.users().messages().get(userId="me", id=message_id, format="full").execute()

        payload = message["payload"]
        headers = payload.get("headers", [])

        # Extract data
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
        body = self._extract_body(payload)

        return {
            "id": message_id,
            "subject": subject,
            "sender": extract_email_address(sender),
            "date": date,  # TODO convert to dt
            "body": body,
        }

    @staticmethod
    def save_email_to_db(
        email_data: dict,
        session: SessionLocal,
    ) -> tuple[JobEmails, bool]:
        """Save email and job IDs to database
        :param email_data: Dictionary containing email metadata
        :param session: SQLAlchemy database session
        :return: JobEmails instance and whether the record was created or already existing"""

        # Check if email already exists
        existing_email = session.query(JobEmails).filter(JobEmails.external_email_id == email_data["id"]).first()

        if existing_email:
            return existing_email, False

        # Create new email record
        # noinspection PyArgumentList
        email_record = JobEmails(
            external_email_id=email_data["id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            date_received=email_data["date"],
            platform="indeed" if "alert@indeed.com" in email_data["body"] else "linkedin",
            owner_id=get_user_id(email_data["sender"], session),
        )
        session.add(email_record)
        session.commit()
        session.refresh(email_record)

        return email_record, True

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    @staticmethod
    def extract_linkedin_job_ids(body: str) -> list[str]:
        """Extract LinkedIn job IDs from the email body"""

        pattern = r"linkedin\.com/(?:comm/)?jobs/view/(\d+)"

        # Find all matches
        job_ids = re.findall(pattern, body, re.IGNORECASE)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(job_ids))

    @staticmethod
    def extract_indeed_job_ids(body: str) -> list[str]:
        """Extract Indeed job advertisement IDs from email body URLs
        :param body: Email body content as string
        :return: List of unique Indeed job advertisement IDs"""

        # Pattern to match both pagead and rc URLs
        pattern = r"https?://(?:uk\.)?indeed\.com/(?:pagead|rc)/clk/dl\?[^>\s]+"

        # Find all matches
        job_urls = re.findall(pattern, body, re.IGNORECASE)

        # Remove duplicates while preserving order
        job_urls = list(dict.fromkeys(job_urls))

        job_ids = []

        for url in job_urls:
            # Try to extract 'ad' parameter first (for pagead URLs)
            ad_match = re.search(r"[?&]ad=([^&>\s]+)", url, re.IGNORECASE)
            if ad_match:
                job_ids.append(ad_match.group(1))
                continue

            # Try to extract 'jk' parameter (for rc URLs)
            jk_match = re.search(r"[?&]jk=([^&>\s]+)", url, re.IGNORECASE)
            if jk_match:
                job_ids.append(jk_match.group(1))

        # Remove duplicates while preserving order
        return list(dict.fromkeys(job_ids))

    @staticmethod
    def save_job_ids_to_db(
        email_record: JobEmails,
        job_ids: list[str],
        platform: str,
        session: SessionLocal,
    ) -> list[JobEmailJobs]:
        """Save extracted job IDs to the database and link them to the email"""

        job_records = []

        for job_id in job_ids:
            # Check if the job already exists for this owner
            existing_job = (
                session.query(JobEmailJobs)
                .filter(
                    JobEmailJobs.external_job_id == job_id,
                    JobEmailJobs.platform == platform,
                    JobEmailJobs.owner_id == email_record.owner_id,
                )
                .first()
            )

            if existing_job:
                # Link email to existing job (if not already linked)
                if email_record not in existing_job.emails:
                    existing_job.emails.append(email_record)
                job_records.append(existing_job)
            else:
                # Create new job record
                # noinspection PyArgumentList
                new_job = JobEmailJobs(
                    external_job_id=job_id,
                    platform=platform,
                    owner_id=email_record.owner_id,
                )

                # Link email to new job
                new_job.emails.append(email_record)

                session.add(new_job)
                job_records.append(new_job)

        session.commit()

        # Refresh all records
        for job_record in job_records:
            session.refresh(job_record)

        return job_records

    def run(self, timedelta_days: int | float = 10) -> dict:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        logger.info("Starting Gmail scraping workflow")

        stats = {
            "start_time": start_time.isoformat(),
            "users_processed": 0,
            "emails_found": 0,
            "emails_processed": 0,
            "emails_new": 0,
            "emails_existing": 0,
            "jobs_extracted": 0,
            "linkedin_jobs": 0,
            "indeed_jobs": 0,
            "errors": [],
            "duration_seconds": 0.0,
        }

        try:
            db = next(get_db())  # TODO add failure log
            users = db.query(User).all()
            logger.info(f"Found {len(users)} users to process")

            for user in users:
                logger.info(f"Processing user: {user.email} (ID: {user.id})")
                stats["users_processed"] += 1

                try:
                    email_ids = self.search_messages(user.email, timedelta_days)
                except Exception as exception:
                    logger.error(f"Failed to search messages due to error: {exception}")
                    continue
                stats["emails_found"] += len(email_ids)

                for email_id in email_ids:
                    logger.info(f"Processing email with ID: {email_id}")
                    try:
                        emails_data = self.get_message_data(email_id)
                    except Exception as exception:
                        logger.error(f"Failed to get email data for email ID {email_id} due to error: {exception}")
                        continue  # next user

                    try:
                        email_record, is_new = self.save_email_to_db(emails_data, db)
                        stats["emails_processed"] += 1
                    except Exception as exception:
                        logger.error(f"Failed to save email data for email ID {email_id} due to error: {exception}")
                        continue  # next user

                    # If the email is not already in the database...
                    if is_new:
                        stats["emails_new"] += 1
                        job_ids, platform = None, None

                        if "linkedin" in emails_data["body"].lower():
                            logger.info(f"Scraping linkedin jobs")
                            job_ids = self.extract_linkedin_job_ids(emails_data["body"])
                            platform = "linkedin"
                            stats["linkedin_jobs"] += len(job_ids)
                        elif "indeed" in emails_data["body"].lower():
                            logger.info(f"Scraping indeed jobs")
                            job_ids = self.extract_indeed_job_ids(emails_data["body"])
                            platform = "indeed"
                            stats["indeed_jobs"] += len(job_ids)

                        if job_ids:
                            try:
                                self.save_job_ids_to_db(email_record, job_ids, platform, db)
                                stats["jobs_extracted"] += len(job_ids)
                                logger.info(f"Extracted {len(job_ids)} job IDs from {platform}")
                            except Exception as exception:
                                logger.warning(
                                    f"Failed to save job IDs for email ID {email_id} due to error: {exception}"
                                )
                                continue  # next email

                        else:
                            logger.info(f"No job IDs found in email: {emails_data['subject']}")
                    else:
                        stats["emails_existing"] += 1
                        logger.info("Email already exists in database")

            # Log final statistics
            stats["end_time"] = datetime.now().isoformat()
            stats["duration_seconds"] = (datetime.now() - start_time).total_seconds()

            AppLogger.log_execution_time(logger, start_time, "Gmail scraping workflow")
            AppLogger.log_stats(logger, stats, "Gmail Scraping Results")

            return stats

        except Exception as exception:
            error_msg = f"Critical error in scraping workflow: {exception}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            stats["end_time"] = datetime.now().isoformat()
            return stats


if __name__ == "__main__":
    gmail = GmailScraper()
    gmail.run()
