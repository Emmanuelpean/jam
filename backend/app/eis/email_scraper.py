"""Gmail Email Retrieval and LinkedIn Job Extraction Module

This module provides functionality to authenticate with Gmail using OAuth 2.0,
retrieve email messages, and extract LinkedIn job IDs from email content.
It offers a complete workflow for accessing Gmail data and parsing job-related
information from email bodies."""

import re
import threading
import traceback
from datetime import datetime

import cloudscraper

from app import models
from app.config import settings
from app.database import session_local
from app.eis.job_scraper import LinkedinJobScraper, IndeedJobScraper, extract_indeed_jobs_from_email
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog
from app.emails.email_service import EmailService
from app.emails.utils import get_user_id_from_email, clean_email_address
from app.utils import get_gmail_logger

logger = get_gmail_logger()


class JobScraper(EmailService):
    """Gmail Scrapper"""

    def __init__(self) -> None:
        """Object constructor"""

        EmailService.__init__(self)

    # ------------------------------------------------- EMAIL READING -------------------------------------------------

    def save_email_to_db(
        self,
        message_id: str,
        sender: str,
        service_log_id: int,
        db,
    ) -> tuple[JobAlertEmail, bool]:
        """Save email and job IDs to database
        :param message_id: Message ID
        :param sender: Sender email address
        :param service_log_id: ID of the EisServiceLog instance associated with this email
        :param db: SQLAlchemy database session
        :return: JobEmails instance and whether the record was created or already existing"""

        message = self.get_email_content(message_id)

        if "linkedin" in message["from"].lower():
            platform = "linkedin"
        elif "indeed" in message["from"].lower():
            platform = "indeed"
        elif "veganjobs" in message["from"].lower():
            platform = "veganjobs"
        else:
            raise ValueError("Email body does not contain a valid platform identifier.")

        # Check if email already exists
        existing_email = db.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == message_id).first()

        # Return the existing record
        if existing_email:
            return existing_email, False

        # Create a new email record
        else:
            # noinspection PyArgumentList
            email_record = JobAlertEmail(
                owner_id=get_user_id_from_email(clean_email_address(sender), db),
                service_log_id=service_log_id,
                external_email_id=message_id,
                subject=message["subject"],
                sender=clean_email_address(sender),
                date_received=message["date"],
                body=message["body"],
                platform=platform,
            )
            db.add(email_record)
            db.commit()
            db.refresh(email_record)

            return email_record, True

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    @classmethod
    def extract_linkedin_job_ids(cls, body: str) -> list[str]:
        """Extract LinkedIn job IDs from the email body
        :param body: Email body content as string
        :return: List of unique LinkedIn job IDs"""

        pattern = r"linkedin\.com/(?:comm/)?jobs/view/(\d+)"
        job_ids = re.findall(pattern, body, re.IGNORECASE)
        return list(dict.fromkeys(job_ids))

    @classmethod
    def get_indeed_redirected_url(cls, job_url: str) -> str:
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

    @classmethod
    def extract_indeed_job_ids(cls, body: str) -> list[str]:
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
                url = cls.get_indeed_redirected_url(url)

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

    @staticmethod
    def save_job_data_to_db(
        job_records: list[ScrapedJob] | ScrapedJob,
        job_data: list[dict] | dict,
        scraped_date: datetime,
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
            record.scrape_datetime = scraped_date
            record.is_scraped = True
            db.commit()

    # ----------------------------------------------------- RUNNER -----------------------------------------------------

    def run_scraping(self, timedelta_days: int | float = 10) -> EisServiceLog:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        logger.info("Starting email scraping workflow")

        with session_local() as db:

            # Service log
            # noinspection PyArgumentList
            service_log_entry = EisServiceLog(
                run_datetime=start_time,
            )
            db.add(service_log_entry)
            db.commit()
            db.refresh(service_log_entry)

            try:
                # Process emails for all users
                jobs_data = self._process_user_emails(db, timedelta_days, service_log_entry)

                # Scrape remaining jobs that haven't been scraped yet
                self._scrape_remaining_jobs(db, service_log_entry, jobs_data)

                # Log final statistics
                service_log_entry.run_duration = (datetime.now() - start_time).total_seconds()
                success = True
                error_message = None
                # AppLogger.log_execution_time(logger, start_time, "Gmail scraping workflow")
                # AppLogger.log_stats(logger, service_log_entry, "Gmail Scraping Results")

            except Exception as exception:
                logger.exception(f"Critical error in scraping workflow: {exception}")
                service_log_entry.run_duration = (datetime.now() - start_time).total_seconds()
                success = False
                error_message = str(exception)

            service_log_entry.is_success = success
            service_log_entry.error_message = error_message
            db.commit()
            return service_log_entry

    def _process_user_emails(
        self,
        db,
        timedelta_days: int | float,
        service_log_entry: EisServiceLog,
    ) -> dict:
        """Process emails for all users
        :param db: Database session
        :param timedelta_days: Number of days to search for emails
        :param service_log_entry: Service log entry"""

        users = db.query(models.User).filter(models.User.toast_active).all()
        logger.info(f"Found {len(users)} users to process")

        # For each user...
        jobs_data = {}
        for user in users:
            logger.info(f"Processing user: {user.email} (ID: {user.id})")

            # Get the list of all emails
            try:
                email_external_ids = self.get_email_ids(settings.scraper_email, user.email, True, timedelta_days)
                service_log_entry.users_processed_n += 1
                service_log_entry.emails_found_n += len(email_external_ids)
            except Exception as exception:
                logger.exception(f"Failed to search messages due to error: {exception}. Skipping user.")
                continue  # next user

            # For each email...
            for email_external_id in email_external_ids:
                logger.info(f"Processing email with ID: {email_external_id}")
                try:
                    email_record, is_new = self.save_email_to_db(
                        email_external_id, user.email, service_log_entry.id, db
                    )

                    # Process jobs if this is a new email
                    if is_new:
                        service_log_entry.emails_saved_n += 1
                        jobs_data.update(self._process_email(db, email_record, service_log_entry))
                    else:
                        logger.info("Email already exists in database. Skipping email.")

                except Exception as exception:
                    message = f"Failed to get and save email data for email ID {email_external_id} due to error: {exception}. Skipping email."
                    logger.exception(message)
                    continue  # next email

        return jobs_data

    def _process_email(
        self,
        db,
        email_record: JobAlertEmail,
        service_log_entry: EisServiceLog,
    ) -> dict:
        """Extract job ids from an email
        :param db: Database session
        :param email_record: JobAlertEmail record
        :param service_log_entry: Service log entry"""

        jobs_data = {}

        # LinkedIn jobs
        if email_record.platform == "linkedin":
            job_ids = self.extract_linkedin_job_ids(email_record.body)
            service_log_entry.linkedin_job_n += len(job_ids)

        # Indeed
        elif email_record.platform == "indeed":

            # Use the email body to extract the job information instead of using the Bright API
            if models.get_setting(db, "indeed_scraper", "brightapi") == "email":
                jobs = extract_indeed_jobs_from_email(email_record.body)
                for job in jobs:
                    try:
                        job_id = self.extract_indeed_job_ids(job["job"]["url"])[0]
                        jobs_data[job_id] = job
                    except Exception as exception:
                        message = f"Failed to extract job ID for job URL {job['job']['url']} due to error: {exception}. Skipping job."
                        logger.exception(message)
                        continue
                job_ids = list(jobs_data.keys())
            else:
                job_ids = self.extract_indeed_job_ids(email_record.body)
            service_log_entry.indeed_job_n += len(job_ids)

        else:
            logger.info(f"No job IDs found in email: {email_record.email_external_id}. Skipping email.")
            return jobs_data

        # Save the extracted job ids to the database
        try:
            self.save_jobs_to_db(email_record, job_ids, db)
            service_log_entry.jobs_extracted_n += len(job_ids)
            logger.info(f"Extracted {len(job_ids)} job IDs from {email_record.platform}")
        except Exception as exception:
            logger.exception(
                f"Failed to save job IDs for email ID {email_record.email_external_id} due to error: {exception}. Skipping email."
            )
            return jobs_data

        return jobs_data

    def _scrape_remaining_jobs(
        self,
        db,
        service_log_entry: EisServiceLog,
        jobs_data: dict,
    ) -> None:
        """Scrape all remaining unscraped jobs
        :param db: Database session
        :param service_log_entry: Service log entry
        :param jobs_data: Dictionary of jobs data"""

        job_records = (
            db.query(ScrapedJob)
            .filter(ScrapedJob.is_scraped.is_(False))
            .filter(ScrapedJob.is_failed.is_(False))
            .distinct(ScrapedJob.external_job_id)
            .all()
        )

        for job_record in job_records:
            if job_record.emails[0].platform == "linkedin":
                scrapper = LinkedinJobScraper(job_record.external_job_id)
            elif job_record.emails[0].platform == "indeed":
                if not models.get_setting(db, "indeed_scraper", "brightapi") == "email":
                    scrapper = IndeedJobScraper(job_record.external_job_id)
                else:
                    scrapper = None
            else:
                logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                continue  # next job record

            # Scrape the data and save them to the database
            logger.info(f"Scraping job ID: {job_record.external_job_id}")
            try:
                if scrapper is not None:
                    job_data = scrapper.scrape_job()
                else:
                    job_data = jobs_data[job_record.external_job_id]
                scrape_datetime = datetime.now()
                self.save_job_data_to_db(job_record, job_data, scrape_datetime, db)
                same_jobs = (
                    db.query(ScrapedJob)
                    .filter(ScrapedJob.is_scraped.is_(False))
                    .filter(ScrapedJob.is_failed.is_(False))
                    .filter(ScrapedJob.external_job_id == job_record.external_job_id)
                    .all()
                )
                for same_job in same_jobs:
                    self.save_job_data_to_db(same_job, job_data, scrape_datetime, db)

                service_log_entry.job_success_n += 1
            except:
                message = f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {traceback.format_exc()}. Skipping job."
                logger.exception(message)
                job_record.is_scraped = True
                job_record.is_failed = True
                job_record.scrape_error = f"{traceback.format_exc()}"
                db.commit()
                service_log_entry.job_fail_n += 1


class GmailScraperService:
    """Service wrapper for GmailScraper with start/stop functionality"""

    def __init__(self) -> None:
        """Initialise the service with a GmailScraper instance."""

        self.scraper = JobScraper()
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
    gmail = JobScraper()
    emails = gmail.get_email_ids("emmanuelpean@gmail.com", inbox_only=True, timedelta_days=2)
    # email_d = gmail.get_email_data(emails[2], "")
    print(emails)
    # print(email_d)
    # gmail.save_email_to_db(email_d, next(get_db()))
    # gmail.run_scraping(2)

    # service = GmailScraperService()
    # service.start()
