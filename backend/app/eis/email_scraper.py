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

from app.database import session_local
from app.eis import schemas
from app.eis.job_scraper import LinkedinJobScraper, IndeedJobScrapper, extract_indeed_jobs_from_email
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog
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
        skip_indeed_scraping: bool = True,
    ) -> None:
        """Object constructor
        :param token_file: Path to the token pickle file
        :param secrets_file: Path to the secrets JSON file containing OAuth credentials
        :param skip_indeed_scraping: if True, use the email content to extract the indeed job data."""

        self.token_file = token_file
        self.secrets_file = secrets_file
        self.skip_indeed_scraping = skip_indeed_scraping
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

    def get_email_ids(
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
        # query += f" from:{sender_email}" if sender_email else ""
        query += f" deliveredto:{sender_email}" if sender_email else ""
        query += " in:inbox" if inbox_only else ""
        query += f" newer_than:{timedelta_days}d" if timedelta_days else ""
        query = query.strip()

        result = self.service.users().messages().list(userId="me", q=query).execute()
        messages = result.get("messages", [])
        return [msg["id"] for msg in messages]

    def _extract_email_body(self, payload: dict) -> str:
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

    def get_email_data(
        self,
        message_id: str,
        sender: str,
    ) -> schemas.JobAlertEmailCreate:
        """Extract readable content from an email
        :param message_id: Message ID
        :param sender: Sender email address
        :return: JobAlertEmailIn object containing email metadata and body content"""

        message = self.service.users().messages().get(userId="me", id=message_id, format="full").execute()

        payload = message["payload"]
        headers = payload.get("headers", [])

        # Extract data
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
        body = self._extract_email_body(payload)

        if "linkedin" in body.lower():
            platform = "linkedin"
        elif "indeed" in body.lower():
            platform = "indeed"
        else:
            raise ValueError("Email body does not contain a valid platform identifier.")

        # Common email date formats to try
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

        return schemas.JobAlertEmailCreate(
            external_email_id=message_id,
            subject=subject,
            sender=clean_email_address(sender),
            date_received=date_received,
            body=body,
            platform=platform,
        )

    @staticmethod
    def save_email_to_db(
        email_data: schemas.JobAlertEmailCreate,
        service_log_id: int,
        db,
    ) -> tuple[JobAlertEmail, bool]:
        """Save email and job IDs to database
        :param email_data: Dictionary containing email metadata
        :param service_log_id: ID of the EisServiceLog instance associated with this email
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
            service_log_id=service_log_id,
            **email_data.model_dump(exclude_unset=True),
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

            # Try to extract 'jk' parameter (for rc URLs)
            jk_match = re.search(r"[?&]jk=([^&>\s]+)", url, re.IGNORECASE)
            if jk_match:
                job_ids.append(jk_match.group(1))

        return list(dict.fromkeys(job_ids))

    @staticmethod
    def save_jobs_to_db(
        email_record: JobAlertEmail,
        job_ids: list[str],
        db,
    ) -> list[ScrapedJob]:
        """Save extracted job IDs to the database and link them to the email
        :param email_record: JobAlertEmail record instance
        :param job_ids: List of job IDs to save
        :param db: SQLAlchemy database session
        :return: List of JobAlertEmailJob instances created or already existing in the database"""

        job_records = []

        for job_id in job_ids:

            # Check if the job already exists for this owner
            existing_entry = (
                db.query(ScrapedJob)
                .filter(
                    ScrapedJob.external_job_id == job_id,
                    ScrapedJob.owner_id == email_record.owner_id,
                )
                .first()
            )

            if not existing_entry:

                # Create new job record
                # noinspection PyArgumentList
                new_job = ScrapedJob(
                    external_job_id=job_id,
                    owner_id=email_record.owner_id,
                )
                new_job.emails.append(email_record)
                db.add(new_job)
                job_records.append(new_job)

            else:
                # Check if this email is already linked to avoid duplicates
                if email_record not in existing_entry.emails:
                    existing_entry.emails.append(email_record)
                job_records.append(existing_entry)

        db.commit()

        # Refresh all records
        for job_record in job_records:
            db.refresh(job_record)

        return job_records

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    @staticmethod
    def save_job_data_to_db(
        job_records: list[ScrapedJob] | ScrapedJob,
        job_data: list[dict] | dict,
        db,
    ) -> None:
        """Save job data to the database"""

        if not isinstance(job_records, list):
            job_records = [job_records]
        if not isinstance(job_data, list):
            job_data = [job_data]

        for job, record in zip(job_data, job_records):
            record.company = job["company"]
            record.location = job["location"]
            record.salary_min = job["job"]["salary"]["min_amount"]
            record.salary_max = job["job"]["salary"]["max_amount"]
            record.title = job["job"]["title"]
            record.description = job["job"]["description"]
            record.url = job["job"]["url"]
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

        with session_local() as db:

            # noinspection PyArgumentList
            service_log_entry = EisServiceLog(
                name="Email Scraper Service",
                run_datetime=start_time,
            )
            db.add(service_log_entry)
            db.commit()
            db.refresh(service_log_entry)

            try:
                users = db.query(User).all()
                logger.info(f"Found {len(users)} users to process")

                # For each user...
                for user in users:
                    logger.info(f"Processing user: {user.email} (ID: {user.id})")

                    # --------------------------------------------- EMAILS ---------------------------------------------

                    # Get the list of all emails
                    try:
                        email_external_ids = self.get_email_ids(user.email, True, timedelta_days)
                        stats["users_processed"] += 1
                    except Exception as exception:
                        logger.exception(f"Failed to search messages due to error: {exception}. Skipping user.")
                        continue
                    stats["emails_found"] += len(email_external_ids)

                    # For each email...
                    for email_external_id in email_external_ids:
                        logger.info(f"Processing email with ID: {email_external_id}")
                        try:
                            email_data = self.get_email_data(email_external_id, user.email)
                            email_record, is_new = self.save_email_to_db(email_data, service_log_entry.id, db)
                        except Exception as exception:
                            message = f"Failed to get and save email data for email ID {email_external_id} due to error: {exception}. Skipping email."
                            logger.exception(message)
                            continue  # next email

                        # -------------------------------------------- JOBS --------------------------------------------

                        # If the email is not already in the database...
                        if is_new:
                            stats["emails_new"] += 1

                            if email_record.platform == "linkedin":
                                # Get the job ids
                                job_ids = self.extract_linkedin_job_ids(email_record.body)
                                stats["linkedin_jobs"] += len(job_ids)

                            elif email_record.platform == "indeed":
                                if self.skip_indeed_scraping:
                                    jobs_ = extract_indeed_jobs_from_email(email_record.body)
                                    jobs = {}
                                    for job in jobs_:
                                        try:
                                            jobs[self.extract_indeed_job_ids(job["job"]["url"])[0]] = job
                                        except Exception as exception:
                                            message = f"Failed to extract job ID for job URL {job['job']['url']} due to error: {exception}. Skipping job."
                                            logger.exception(message)
                                            continue
                                    job_ids = list(jobs.keys())
                                else:
                                    job_ids = self.extract_indeed_job_ids(email_record.body)
                                stats["indeed_jobs"] += len(job_ids)

                            else:
                                logger.info(f"No job IDs found in email: {email_external_id}. Skipping email.")
                                continue  # next email

                            # Save the extracted job ids to the database
                            try:
                                job_records = self.save_jobs_to_db(email_record, job_ids, db)
                                stats["jobs_extracted"] += len(job_ids)
                                logger.info(f"Extracted {len(job_ids)} job IDs from {email_record.platform}")
                            except Exception as exception:
                                message = f"Failed to save job IDs for email ID {email_external_id} due to error: {exception}. Skipping email."
                                logger.exception(message)
                                continue  # next email


                            # For indeed jobs, immediately save the extracted content
                            if email_record.platform == "indeed" and self.skip_indeed_scraping:
                                print(jobs)
                                for job_record in job_records:
                                    try:
                                        self.save_job_data_to_db(job_record, jobs[job_record.external_job_id], db)
                                        stats["jobs_scraped"] += 1
                                    except Exception as exception:
                                        message = f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {exception}. Skipping job."
                                        logger.exception(message)
                                        job_record.is_scraped = True
                                        job_record.error_msg = f"{str(exception)}"
                                        db.commit()
                                        stats["jobs_failed"] += 1
                                        continue  # next job
                        else:
                            stats["emails_existing"] += 1
                            logger.info("Email already exists in database. Skipping email.")

                # -------------------------------------------- JOB SCRAPPING -------------------------------------------

                # Get all the job ids from the table and scrape them
                job_records = db.query(ScrapedJob).filter(ScrapedJob.is_scraped.is_(False)).all()

                for job_record in job_records:
                    if job_record.emails[0].platform == "linkedin":
                        scrapper = LinkedinJobScraper(job_record.external_job_id)
                    elif job_record.emails[0].platform == "indeed" and not self.skip_indeed_scraping:
                        scrapper = IndeedJobScrapper(job_record.external_job_id)
                    else:
                        logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                        continue  # next job record

                    # Scrap the data and save them to the database
                    logger.info(f"Scraping job ID: {job_record.external_job_id}")
                    try:
                        job_data = scrapper.scrape_job()
                        self.save_job_data_to_db(job_record, job_data, db)
                        stats["jobs_scraped"] += 1
                    except Exception as exception:
                        message = f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {exception}. Skipping job."
                        logger.exception(message)
                        job_record.is_scraped = True
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

            service_log_entry.is_success = success
            service_log_entry.error_message = error_message
            service_log_entry.job_success_n = stats["jobs_scraped"]
            service_log_entry.job_fail_n = stats["jobs_failed"]
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
            logger.info("Service is already running")
            return

        self.is_running = True
        self.stop_event.clear()

        # Start the service in a separate thread
        self.thread = threading.Thread(target=self._run_service, args=(period_hours,))
        self.thread.daemon = False
        self.thread.start()

        logger.info(f"Gmail scraping service started with {period_hours}h interval")

    def stop(self) -> None:
        """Stop the scraping service"""

        if not self.is_running:
            logger.info("Service is not running")
            return

        logger.info("Stopping Gmail scraping service...")
        self.is_running = False
        self.stop_event.set()

        if self.thread:
            while self.thread.is_alive():
                self.thread.join(timeout=5)  # Wait up to 5 seconds for clean shutdown

        logger.info("Gmail scraping service stopped")

    def _run_service(self, period_hours: float) -> None:
        """Internal method that runs the scraping loop
        :param period_hours: Hours between each scraping run"""

        while self.is_running and not self.stop_event.is_set():
            try:
                logger.info(f"[{datetime.now()}] Starting scraping run...")

                # Run the scraping
                result = self.scraper.run_scraping(timedelta_days=2)

                duration = result.get("duration_seconds", 0)
                sleep_time = max([0, period_hours * 3600 - duration])
                logger.info(f"[{datetime.now()}] Scraping completed in {duration:.2f}s. Sleeping for {sleep_time:.2f}s")
                if self.stop_event.wait(timeout=sleep_time):
                    break

            except Exception as e:
                logger.info(f"[{datetime.now()}] Error in scraping service: {e}")
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
    emails = gmail.get_email_ids("emmanuelpean@gmail.com", inbox_only=True, timedelta_days=2)
    email_d = gmail.get_email_data(emails[0], "")
    print(email_d.body)
    # print(email_d)
    # gmail.save_email_to_db(email_d, next(get_db()))
    # gmail.run_scraping(2)

    # service = GmailScraperService()
    # service.start()

    # gmail = GmailScraper()
