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
import threading
from datetime import datetime
from email.utils import parseaddr

import cloudscraper
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.database import SessionLocal
from app.eis.job_scraper import LinkedinJobScraper, IndeedScrapper
from app.eis.models import JobAlertEmail, JobScraped, ServiceLog, Email
from app.models import User
from app.utils import get_gmail_logger, AppLogger

logger = get_gmail_logger()


def clean_email_address(sender_field: str) -> str:
    """Extract a clean email address from the sender field
    Handles formats like:
    - 'John Doe <john.doe@gmail.com>'
    - 'john.doe@gmail.com'
    - '"John Doe" <john.doe@gmail.com>'"""

    name, email = parseaddr(sender_field)
    return email.lower().strip() if email else sender_field.lower().strip()


def get_user_id_from_email(email: str, db) -> None | int:
    """Get user id from email"""

    entry = db.query(User).filter(User.email == email).first()
    if entry:
        return entry.id
    else:
        raise AssertionError(f"User with email '{email}' not found in database.")


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
            raise FileNotFoundError(f"Secrets file '{self.secrets_file}' not found.")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid JSON format in secrets file '{self.secrets_file}': {e}")

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

    # ------------------------------------------------- EMAIL READING -------------------------------------------------

    def search_messages(
        self,
        sender_email: str = "",
        inbox_only: bool = True,
        timedelta_days: int | float = 1,
    ) -> list[str]:
        """Search for messages matching a query
        :param sender_email: Sender email address
        :param inbox_only: Search only in the inbox
        :param timedelta_days: Number of days to search for emails
        :return: List of message IDs matching the query"""

        query = ""
        query += f"from:{sender_email}" if sender_email else ""
        query += " in:inbox" if inbox_only else ""
        query += f" newer_than:{timedelta_days}d" if timedelta_days else ""
        query = query.strip()

        result = self.service.users().messages().list(userId="me", q=query).execute()
        messages = result.get("messages", [])
        return [msg["id"] for msg in messages]

    def _extract_body(self, payload: dict) -> str:
        """Extract email body from payload
        :param payload: Email payload dictionary
        :return: Email body content as a string"""

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

    def get_message_data(self, message_id: str) -> Email:
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

        if "linkedin" in body.lower():
            platform = "linkedin"
        elif "indeed" in body.lower():
            platform = "indeed"
        else:
            raise ValueError("Email body does not contain a valid platform identifier.")

        return Email(
            external_email_id=message_id,
            subject=subject,
            sender=clean_email_address(sender),
            date_received=datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z"),
            body=body,
            platform=platform,
        )

    @staticmethod
    def save_email_to_db(
        email_data: Email,
        db: SessionLocal,
    ) -> tuple[JobAlertEmail, bool]:
        """Save email and job IDs to database
        :param email_data: Dictionary containing email metadata
        :param db: SQLAlchemy database session
        :return: JobEmails instance and whether the record was created or already existing"""

        # Check if email already exists
        existing_email = (
            db.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email_data.external_email_id).first()
        )

        if existing_email:
            return existing_email, False

        # Create new email record
        # noinspection PyArgumentList
        email_record = JobAlertEmail(
            owner_id=get_user_id_from_email(email_data.sender, db),
            **email_data.model_dump(),
        )
        db.add(email_record)
        db.commit()
        db.refresh(email_record)

        return email_record, True

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    @staticmethod
    def extract_linkedin_job_ids(body: str) -> list[str]:
        """Extract LinkedIn job IDs from the email body
        :param body: Email body content as string
        :return: List of unique LinkedIn job IDs"""

        pattern = r"linkedin\.com/(?:comm/)?jobs/view/(\d+)"
        job_ids = re.findall(pattern, body, re.IGNORECASE)
        return list(dict.fromkeys(job_ids))

    @staticmethod
    def get_indeed_redirected_url(job_url: str) -> str:
        """Get the redirected URL from the Indeed job URL
        :param job_url: Indeed job URL
        :return: Redirected URL"""

        scraper = cloudscraper.create_scraper()
        response = scraper.get(job_url, allow_redirects=True)
        max_attempts = 100
        iteration = 0
        while "indeed.com/viewjob?jk" not in response.url:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(job_url, allow_redirects=True)
            iteration += 1
            if iteration > max_attempts:
                break
        return response.url

    def extract_indeed_job_ids(self, body: str) -> list[str]:
        """Extract Indeed job advertisement IDs from email body URLs
        :param body: Email body content as string
        :return: List of unique Indeed job IDs"""

        pattern = r"https?://(?:uk\.)?indeed\.com/(?:pagead|rc)/clk/dl\?[^>\s]+"
        job_urls = re.findall(pattern, body, re.IGNORECASE)
        job_urls = list(dict.fromkeys(job_urls))
        job_ids = []

        for url in job_urls:
            # Try to extract 'ad' parameter first (for pagead URLs)
            ad_match = re.search(r"[?&]mo=([^&>\s]+)", url, re.IGNORECASE)
            if ad_match:
                url = self.get_indeed_redirected_url(url)
                print(url)

            # Try to extract 'jk' parameter (for rc URLs)
            jk_match = re.search(r"[?&]jk=([^&>\s]+)", url, re.IGNORECASE)
            if jk_match:
                job_ids.append(jk_match.group(1))

        print(len(job_ids))
        return list(dict.fromkeys(job_ids))

    @staticmethod
    def save_job_to_db(
        email_record: JobAlertEmail,
        job_ids: list[str],
        db: SessionLocal,
    ) -> list[JobScraped]:
        """Save extracted job IDs to the database and link them to the email
        :param email_record: JobAlertEmail record instance
        :param job_ids: List of job IDs to save
        :param db: SQLAlchemy database session
        :return: List of JobAlertEmailJob instances created or already existing in the database"""

        job_records = []

        for job_id in job_ids:

            # Check if the job already exists for this owner
            existing_entry = (
                db.query(JobScraped)
                .filter(
                    JobScraped.external_job_id == job_id,
                    JobScraped.owner_id == email_record.owner_id,
                    JobScraped.email_id == email_record.id,
                )
                .first()
            )

            if not existing_entry:

                # Create new job record
                # noinspection PyArgumentList
                new_job = JobScraped(
                    external_job_id=job_id,
                    owner_id=email_record.owner_id,
                    email_id=email_record.id,
                )

                db.add(new_job)
                job_records.append(new_job)

        db.commit()

        # Refresh all records
        for job_record in job_records:
            db.refresh(job_record)

        return job_records

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    @staticmethod
    def save_job_json_to_db(
        job_records: list[JobScraped],
        job_data: list[dict],
        db: SessionLocal,
    ) -> None:
        """Save job data to the database"""

        if not isinstance(job_records, list):
            job_records = [job_records]
        if not isinstance(job_data, list):
            job_data = [job_data]

        for job, record in zip(job_data, job_records):

            record.company_name = job_data["company"]
            record.location = job_data["location"]
            record.salary_min = job_data["salary"]["min_amount"]
            record.salary_max = job_data["salary"]["max_amount"]
            record.job_title = job_data["job"]["title"]
            record.job_description = job_data["job"]["description"]
            record.job_url = job_data["job"]["url"]
            record.is_scraped = True
            db.commit()

    def run_scraping(self, timedelta_days: int | float = 10) -> dict:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        logger.info("Starting email scraping workflow")

        stats = {
            "start_time": start_time.isoformat(),
            "users_processed": 0,
            "emails_found": 0,
            "emails_saved": 0,
            "emails_new": 0,
            "emails_existing": 0,
            "jobs_extracted": 0,
            "jobs_failed": 0,
            "jobs_scraped": 0,
            "linkedin_jobs": 0,
            "indeed_jobs": 0,
            "duration_seconds": 0.0,
        }

        with SessionLocal() as db:

            try:
                users = db.query(User).all()
                logger.info(f"Found {len(users)} users to process")

                # For each user...
                for user in users:
                    logger.info(f"Processing user: {user.email} (ID: {user.id})")

                    # Get the list of all emails
                    try:
                        email_external_ids = self.search_messages(user.email, True, timedelta_days)
                        stats["users_processed"] += 1
                    except Exception as exception:
                        logger.exception(f"Failed to search messages due to error: {exception}. Skipping user.")
                        continue
                    stats["emails_found"] += len(email_external_ids)

                    # For each email...
                    for email_external_id in email_external_ids:
                        logger.info(f"Processing email with ID: {email_external_id}")
                        try:
                            email_data = self.get_message_data(email_external_id)
                        except Exception as exception:
                            logger.exception(
                                f"Failed to get email data for email ID {email_external_id} due to error: {exception}. Skipping email."
                            )
                            continue  # next email

                        # Save the email data
                        try:
                            logger.info(f"Saving email: {email_data.subject}")
                            email_record, is_new = self.save_email_to_db(email_data, db)
                            stats["emails_saved"] += 1
                        except Exception as exception:
                            logger.exception(
                                f"Failed to save email data for email ID {email_external_id} due to error: {exception}. Skipping email."
                            )
                            continue  # next email

                        # If the email is not already in the database...
                        if is_new:
                            stats["emails_new"] += 1

                            if email_record.platform == "linkedin":
                                job_ids = self.extract_linkedin_job_ids(email_record.body)
                                stats["linkedin_jobs"] += len(job_ids)
                            elif email_record.platform == "indeed":
                                job_ids = self.extract_indeed_job_ids(email_record.body)
                                stats["indeed_jobs"] += len(job_ids)
                            else:
                                logger.info(f"No job IDs found in email: {email_external_id}. Skipping email.")
                                continue  # next email

                            # Save the retrieved job ids to the database
                            try:
                                self.save_job_to_db(email_record, job_ids, db)
                                stats["jobs_extracted"] += len(job_ids)
                                logger.info(f"Extracted {len(job_ids)} job IDs from {email_record.platform}")
                            except Exception as exception:
                                logger.exception(
                                    f"Failed to save job IDs for email ID {email_external_id} due to error: {exception}. Skipping email."
                                )
                                continue  # next email
                        else:
                            stats["emails_existing"] += 1
                            logger.info("Email already exists in database. Skipping email.")

                # Get all the job ids from the table and scrape them
                job_records = (
                    db.query(JobScraped)
                    .filter(JobScraped.is_scraped.is_(False))
                    .distinct(JobScraped.external_job_id)
                    .all()
                )

                for job_record in job_records:
                    if job_record.emails[0].platform == "linkedin":
                        scrapper = LinkedinJobScraper(job_record.external_job_id)
                    elif job_record.emails[0].platform == "indeed":
                        scrapper = IndeedScrapper(job_record.external_job_id)
                    else:
                        logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                        continue  # next job record
                    logger.info(f"Scraping job ID: {job_record.external_job_id}")
                    try:
                        job_data = scrapper.scrape_job()
                        self.save_job_json_to_db(job_record, job_data, db)
                        stats["jobs_scraped"] += 1
                    except Exception as exception:
                        logger.exception(
                            f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {exception}. Skipping job."
                        )
                        job_record.error_msg = f"{str(exception)}"
                        db.commit()
                        stats["jobs_failed"] += 1
                        continue  # next job

                # Log final statistics
                stats["end_time"] = datetime.now().isoformat()
                stats["duration_seconds"] = (datetime.now() - start_time).total_seconds()
                success = True
                error_message = None
                AppLogger.log_execution_time(logger, start_time, "Gmail scraping workflow")
                AppLogger.log_stats(logger, stats, "Gmail Scraping Results")

            except Exception as exception:
                logger.exception(f"Critical error in scraping workflow: {exception}")
                stats["end_time"] = datetime.now().isoformat()
                success = False
                error_message = str(exception)

            entry = ServiceLog(
                name="EIS",
                run_duration=stats["duration_seconds"],
                run_datetime=start_time,
                is_success=success,
                error_message=error_message,
                job_success_n=stats["jobs_scraped"],
                job_fail_n=stats["jobs_failed"],
            )
            db.add(entry)
            db.commit()

            return stats


class GmailScraperService:
    """Service wrapper for GmailScraper with start/stop functionality"""

    def __init__(self) -> None:
        """Initialize the service with a GmailScraper instance."""

        self.scraper = GmailScraper()
        self.is_running = False
        self.thread = None
        self.stop_event = threading.Event()

    def start(self, period_hours: float = 3.0) -> None:
        """Start the scraping service
        :param period_hours: Hours between each scraping run"""

        if self.is_running:
            print("Service is already running")
            return

        self.is_running = True
        self.stop_event.clear()

        # Start the service in a separate thread
        self.thread = threading.Thread(target=self._run_service, args=(period_hours,))
        self.thread.daemon = False
        self.thread.start()

        print(f"Gmail scraping service started with {period_hours}h interval")

    def stop(self) -> None:
        """Stop the scraping service"""

        if not self.is_running:
            print("Service is not running")
            return

        print("Stopping Gmail scraping service...")
        self.is_running = False
        self.stop_event.set()

        if self.thread:
            while self.thread.is_alive():
                self.thread.join(timeout=5)  # Wait up to 5 seconds for clean shutdown

        print("Gmail scraping service stopped")

    def _run_service(self, period_hours: float) -> None:
        """Internal method that runs the scraping loop
        :param period_hours: Hours between each scraping run"""

        while self.is_running and not self.stop_event.is_set():
            try:
                print(f"[{datetime.now()}] Starting scraping run...")

                # Run the scraping
                result = self.scraper.run_scraping(timedelta_days=2)

                duration = result.get("duration_seconds", 0)
                sleep_time = max([0, period_hours * 3600 - duration])
                print(f"[{datetime.now()}] Scraping completed in {duration:.2f}s. Sleeping for {sleep_time:.2f}s")
                if self.stop_event.wait(timeout=sleep_time):
                    break

            except Exception as e:
                print(f"[{datetime.now()}] Error in scraping service: {e}")
                # Sleep for a shorter time on error to retry sooner
                if self.stop_event.wait(timeout=300):  # 5 minutes
                    break

    def status(self) -> dict:
        """Get the current status of the service"""

        return {
            "is_running": self.is_running,
            "thread_alive": self.thread.is_alive() if self.thread else False,
            "thread_name": self.thread.name if self.thread else None,
        }


if __name__ == "__main__":
    gmail = GmailScraper()
    # emails = gmail.search_messages("emmanuelpean@gmail.com", 10)
    # email_d = gmail.get_message_data(emails[0])
    # gmail.save_email_to_db(email_d, next(get_db()))
    gmail.run_scraping(10)

    # service = GmailScraperService()
    # service.start()

    # gmail = GmailScraper()
