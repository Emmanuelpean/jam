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

import cloudscraper
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app import schemas
from app.database import get_db, SessionLocal
from app.eis.job_scraper import LinkedinJobScraper, IndeedScrapper
from app.eis.location_parser import LocationParser
from app.eis.models import JobAlertEmail, JobAlertEmailJob, JobScraped, CompanyScraped, LocationScraped
from app.models import Company, User
from app.utils import get_gmail_logger, AppLogger


class Email(schemas.BaseModel):
    """Email model"""

    external_email_id: str
    subject: str
    sender: str
    date_received: datetime
    body: str
    platform: str


class EmailOut(Email):
    """Email model with ID"""

    owner_id: int


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
    def save_job_ids_to_db(
        email_record: JobAlertEmail,
        job_ids: list[str],
        db: SessionLocal,
    ) -> list[JobAlertEmailJob]:
        """Save extracted job IDs to the database and link them to the email
        :param email_record: JobAlertEmail record instance
        :param job_ids: List of job IDs to save
        :param db: SQLAlchemy database session
        :return: List of JobAlertEmailJob instances created or already existing in the database"""

        job_records = []

        for job_id in job_ids:

            # Check if the job already exists for this owner
            existing_entry = (
                db.query(JobAlertEmailJob)
                .filter(
                    JobAlertEmailJob.external_job_id == job_id,
                    JobAlertEmailJob.owner_id == email_record.owner_id,
                    JobAlertEmailJob.email_id == email_record.id,
                )
                .first()
            )

            if not existing_entry:

                # Create new job record
                # noinspection PyArgumentList
                new_job = JobAlertEmailJob(
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
        job_records: list[JobAlertEmailJob],
        job_data: list[dict],
        db: SessionLocal,
    ) -> None:
        """Save job data to the database"""

        if not isinstance(job_records, list):
            job_records = [job_records]
        if not isinstance(job_data, list):
            job_data = [job_data]

        for job, record in zip(job_data, job_records):

            # Save the company
            company = (
                db.query(Company)
                .filter(Company.owner_id == record.email.owner_id, Company.name == job.get("company_name"))
                .first()
            )
            if not company:
                # noinspection PyArgumentList
                company = CompanyScraped(
                    name=job.get("company"),
                    owner_id=record.email.owner_id,
                )
            db.add(company)
            db.commit()
            db.refresh(company)

            # Save the location
            parser = LocationParser()
            parsed_location = parser.parse_location(job.get("location"))

            # noinspection PyArgumentList
            location = LocationScraped(
                **parsed_location.model_dump(),
                owner_id=record.email.owner_id,
            )
            db.add(location)
            db.commit()
            db.refresh(location)

            # noinspection PyArgumentList
            job_record = JobScraped(
                title=job["job"]["title"],
                description=job["job"]["description"],
                url=job["job"]["url"],
                salary_min=job["job"]["salary"]["min_amount"],
                salary_max=job["job"]["salary"]["max_amount"],
                owner_id=record.email.owner_id,
                location_id=location.id,
                company_id=company.id,
                jobalertemailjob_id=record.id,
            )
            db.add(job_record)
            db.commit()

    def run(self, timedelta_days: int | float = 10) -> dict:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        logger.info("Starting email scraping workflow")

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
            "duration_seconds": 0.0,
        }

        try:
            db = next(get_db())
            users = db.query(User).all()
            logger.info(f"Found {len(users)} users to process")

            # For each user...
            for user in users:
                logger.info(f"Processing user: {user.email} (ID: {user.id})")
                stats["users_processed"] += 1

                # Get the list of all emails
                try:
                    email_external_ids = self.search_messages(user.email, True, timedelta_days)
                except Exception as exception:
                    logger.exception(f"Failed to search messages due to error: {exception}")
                    continue
                stats["emails_found"] += len(email_external_ids)

                # For each email...
                for email_external_id in email_external_ids:
                    logger.info(f"Processing email with ID: {email_external_id}")
                    try:
                        emails_record = self.get_message_data(email_external_id)
                    except Exception as exception:
                        logger.exception(
                            f"Failed to get email data for email ID {email_external_id} due to error: {exception}"
                        )
                        continue  # next user

                    # Get the email data
                    try:
                        email_record, is_new = self.save_email_to_db(emails_record, db)
                        stats["emails_processed"] += 1
                    except Exception as exception:
                        logger.exception(
                            f"Failed to save email data for email ID {email_external_id} due to error: {exception}"
                        )
                        continue  # next user

                    # If the email is not already in the database...
                    if is_new:
                        stats["emails_new"] += 1

                        if email_record.platform == "linkedin":
                            logger.info(f"Scraping Linkedin jobs")
                            job_ids = self.extract_linkedin_job_ids(emails_record.body)
                            stats["linkedin_jobs"] += len(job_ids)
                        elif email_record.platform == "indeed":
                            logger.info(f"Scraping Indeed jobs")
                            job_ids = self.extract_indeed_job_ids(emails_record.body)
                            stats["indeed_jobs"] += len(job_ids)
                        else:
                            logger.info(f"No job IDs found in email: {emails_record.body}")
                            continue

                        # Save the retrieved job ids to the database
                        try:
                            self.save_job_ids_to_db(email_record, job_ids, db)
                            stats["jobs_extracted"] += len(job_ids)
                            logger.info(f"Extracted {len(job_ids)} job IDs from {email_record.platform}")
                        except Exception as exception:
                            logger.exception(
                                f"Failed to save job IDs for email ID {email_external_id} due to error: {exception}"
                            )
                            continue
                    else:
                        stats["emails_existing"] += 1
                        logger.info("Email already exists in database")

            # Get all the job ids from the table and scrape them
            job_records = db.query(JobAlertEmailJob).filter(JobAlertEmailJob.is_scraped.is_(False)).all()
            linkedin_jobs_records = [job for job in job_records if job.email.platform == "linkedin"]
            indeed_job_records = [job for job in job_records if job.email.platform == "indeed"]

            for job_records, scrapper_class in zip([linkedin_jobs_records, indeed_job_records], [LinkedinJobScraper, IndeedScrapper]):
                # job_ids = [job.external_job_id for job in job_records]
                # max_batch_jobs = 1000
                # job_ids = [job_ids[i : i + max_batch_jobs] for i in range(0, len(job_ids), max_batch_jobs)]
                for job_record in job_records:
                    scrapper = scrapper_class(job_record.external_job_id)
                    print(f"Scraping job ID: {job_record}")
                    try:
                        job_data = scrapper.scrape_job()
                        self.save_job_json_to_db(job_record, job_data, db)
                        job_record.is_scraped = True
                        db.commit()
                    except Exception as exception:
                        logger.exception(
                            f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {exception}"
                        )
                        job_record.error_msg = f"Failed to scrape job data: {str(exception)}"
                        job_records.is_scraped = True
                        continue

            # Log final statistics
            stats["end_time"] = datetime.now().isoformat()
            stats["duration_seconds"] = (datetime.now() - start_time).total_seconds()

            AppLogger.log_execution_time(logger, start_time, "Gmail scraping workflow")
            AppLogger.log_stats(logger, stats, "Gmail Scraping Results")

            return stats

        except Exception as exception:
            logger.exception(f"Critical error in scraping workflow: {exception}")
            stats["end_time"] = datetime.now().isoformat()
            return stats

    # def run1(self, period):
    #
    #     while True:
    #         res = self.run(period)
    #         time.sleep(max([0, period * 60 * 60 - res["duration_seconds"]]))


if __name__ == "__main__":
    gmail = GmailScraper()
    # emails = gmail.search_messages("emmanuelpean@gmail.com", 10)
    # email_d = gmail.get_message_data(emails[0])
    # gmail.save_email_to_db(email_d, next(get_db()))
    gmail.run(10)
