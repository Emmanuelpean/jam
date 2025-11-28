"""Email scraper service.

Reads job alert emails from a shared inbox, extracts job IDs for supported
platforms (linkedin, indeed, veganjobs), stores email and job metadata in the
database, scrapes full job details (via platform scrapers or from email
content), and records run statistics in an EisServiceLog."""

import threading
import traceback
from datetime import datetime
import time
from app import models, utils
from app.config import settings
from app.database import get_db
from app.eis.email_parser import extract_linkedin_job_ids, extract_indeed_job_ids, extract_veganjobs_job_ids
from app.eis.job_scraper import (
    LinkedinBrightdataJobScraper,
    IndeedBrightdataJobScraper,
    VeganJobsJobScraper,
    extract_indeed_jobs_from_email,
    JobResult,
)
from app.eis.location_parser import LocationParser
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog
from app.emails.email_service import EmailService
from app.utils import AppLogger

PLATFORMS = ["linkedin", "indeed", "veganjobs"]


class JobEmailScraper(EmailService):
    """Job Email Alert Scraper"""

    def __init__(self, db=None) -> None:
        """Object constructor
        :param db: optional database session for testing"""

        EmailService.__init__(self)
        self.location_parser = LocationParser()
        self.logger = AppLogger.create_service_logger("email_scraper", "INFO")
        self.db = next(get_db()) if db is None else db
        self.countries = utils.open_json("app/data/countries.json")
        self.currencies = utils.open_json("app/data/currencies.json")

    @property
    def indeed_brightapi_setting(self) -> str:
        """Get the Indeed BrightAPI setting from the database"""

        return models.get_setting(self.db, "indeed_scraper", "email")

    def create_service_log(self, **kwargs) -> EisServiceLog:
        """Create a new service log entry
        :param kwargs: EisServiceLog keyword arguments"""

        # noinspection PyArgumentList
        service_log_entry = EisServiceLog(**kwargs)
        self.db.add(service_log_entry)
        self.db.commit()
        self.db.refresh(service_log_entry)
        return service_log_entry

    # ------------------------------------------------ EMAIL PROCESSING ------------------------------------------------

    def get_and_save_email_to_db(
        self,
        email_id: str,
        user: models.User,
        service_log_id: int,
    ) -> tuple[JobAlertEmail, bool]:
        """Read and save an email to the database
        :param email_id: Email ID
        :param user: User entry associated with this email
        :param service_log_id: ID of the EisServiceLog instance associated with this email
        :return: JobEmails instance and whether the record was created or already existing"""

        # Check if the email already exists and return it if it does
        existing_email = self.db.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == email_id).first()

        # Return the existing email
        if existing_email:
            return existing_email, False

        else:

            # Read the email content and determine the platform
            message = self.get_email_data(email_id)

            # Determine the platform
            platform = None
            for plat in PLATFORMS:
                if plat.lower() in message["from"].lower():
                    platform = plat
            if not platform:
                raise ValueError("Email body does not contain a valid platform identifier.")

            # Create a new email record
            # noinspection PyArgumentList
            email_record = JobAlertEmail(
                owner_id=user.id,
                service_log_id=service_log_id,
                external_email_id=email_id,
                subject=message["subject"],
                sender=message["to"],
                date_received=message["date"],
                body=message["body"],
                platform=platform,
            )
            self.db.add(email_record)
            self.db.commit()
            self.db.refresh(email_record)

            # Delete the email from the inbox after saving to DB
            # self.delete_email(message_id)  # TODO to uncomment

            return email_record, True

    # ------------------------------------------------- JOB PROCESSING -------------------------------------------------

    def save_job_base_info_to_db(
        self,
        email_record: JobAlertEmail,
        job_ids: list[str],
    ) -> list[ScrapedJob]:
        """Save extracted job IDs from an email to the database and link them to the email.
        If they already exist, just link them to the email.
        :param email_record: associated JobAlertEmail record instance
        :param job_ids: list of job IDs to save
        :return: list of ScrapedJob instances created or already existing in the database"""

        job_records = []

        for job_id in job_ids:

            # Check if the job already exists for this owner
            existing_entry = (
                self.db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_id)
                .filter(ScrapedJob.owner_id == email_record.owner_id)
                .first()
            )

            # Create new job record if it doesn't exist
            if not existing_entry:
                # noinspection PyArgumentList
                new_job = ScrapedJob(
                    external_job_id=job_id,
                    platform=email_record.platform,
                    owner_id=email_record.owner_id,
                )
                new_job.emails.append(email_record)
                self.db.add(new_job)
                job_records.append(new_job)

            # Link existing job record to the email
            else:
                # Check if this email is already linked to avoid duplicates
                if email_record not in existing_entry.emails:
                    existing_entry.emails.append(email_record)
                job_records.append(existing_entry)

        # Commit and refresh the records
        self.db.commit()
        for job_record in job_records:
            self.db.refresh(job_record)

        return job_records

    def update_scraped_job_data(
        self,
        job_record: ScrapedJob,
        job_data: JobResult,
    ) -> None:
        """Update the job records with the scraped data
        :param job_record: ScrapedJob instance
        :param job_data: scraped job data"""

        # Location & attendance type
        location, attendance_type = self.location_parser.parse_location(job_data.location)
        job_record.location = job_data.location
        job_record.location_postcode = location.postcode
        job_record.location_city = location.city
        job_record.attendance_type = attendance_type
        if location.country:
            for country in self.countries:
                if location.country.lower() == country["name"].lower():
                    job_record.location_country = country["name"]
                    break

        # Salary
        job_record.salary_min = job_data.job.salary.min_amount
        job_record.salary_max = job_data.job.salary.max_amount
        currency_code = (job_data.job.salary.currency or "").lower()
        for currency in self.currencies:
            if currency_code in (currency["code"].lower(), currency["symbol_native"].lower()):
                job_record.salary_currency_name = currency["code"]
                break

        # Job details
        job_record.title = job_data.job.title
        job_record.description = job_data.job.description
        job_record.url = job_data.job.url
        job_record.company = job_data.company

        # Scraping information
        job_record.scrape_datetime = datetime.now()
        job_record.is_scraped = True

        self.db.commit()

    def copy_existing_entry(
        self,
        job_record1: ScrapedJob,
        job_record2: ScrapedJob,
    ) -> ScrapedJob:
        """Copy the data from job_record1 to job_record2
        :param job_record1: Source ScrapedJob instance
        :param job_record2: Target ScrapedJob instance
        :return: Updated job_record2 instance"""

        columns = [
            "company",
            "salary_currency",
            "platform",
            "location",
            "location_city",
            "location_country",
            "location_postcode",
            "attendance_type",
            "salary_min",
            "salary_max",
            "title",
            "description",
            "url",
            "scrape_datetime",
            "is_scraped",
            "is_failed",
            "scrape_error",
        ]
        for key in columns:
            setattr(job_record2, key, getattr(job_record1, key))
        self.db.commit()
        return job_record2

    # ----------------------------------------------------- RUNNER -----------------------------------------------------

    def run_scraping(self, timedelta_days: int | float = 10) -> EisServiceLog:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        self.logger.info("Starting email scraping workflow")
        service_log = self.create_service_log(run_datetime=start_time)

        try:
            # Process emails for all users
            jobs_data = self.process_emails(timedelta_days, service_log)

            # Scrape remaining jobs that haven't been scraped yet
            self.scrape_jobs(service_log, jobs_data)

            # Log final statistics
            service_log.run_duration = (datetime.now() - start_time).total_seconds()
            service_log.is_success = True

        except Exception as exception:
            self.logger.exception(f"Critical error in scraping workflow: {exception}")
            service_log.run_duration = (datetime.now() - start_time).total_seconds()
            service_log.is_success = False
            service_log.error_message = str(exception)
        finally:
            self.logger.info("Finished email scraping workflow")

        self.db.commit()
        return service_log

    def process_emails(
        self,
        timedelta_days: int | float,
        service_log_entry: EisServiceLog,
    ) -> dict:
        """For each user, get and save each new email, then extract the job ids and job data.
        :param timedelta_days: Number of days to search for emails
        :param service_log_entry: EIS Service log entry"""

        # Get the list of active users with TOAST active
        users = self.db.query(models.User).filter(models.User.toast_active, models.User.is_active).all()
        self.logger.info(f"Found {len(users)} users to process.")
        service_log_entry.users_found_n = len(users)
        jobs_data = {platform: {} for platform in PLATFORMS}

        # For each user...
        for user in users:
            self.logger.info(f"Processing user: {user.email} (ID: {user.id})")

            # Get the list of all emails
            try:
                email_ids = self.get_email_ids(
                    recipient_email=settings.scraper_email,
                    sender_email=user.email,
                    inbox_only=True,
                    timedelta_days=timedelta_days,
                )
                service_log_entry.users_processed_n += 1
                service_log_entry.emails_found_n += len(email_ids)
                self.logger.info(f"Found {len(email_ids)} emails")
            except Exception as exception:
                self.logger.exception(f"Failed to search messages due to error: {exception}. Skipping user.")
                continue  # next user

            # For each email...
            for email_id in email_ids:
                self.logger.info(f"Processing email with ID: {email_id}")
                try:
                    email_record, is_new = self.get_and_save_email_to_db(email_id, user, service_log_entry.id)

                    # Process jobs if this is a new email
                    if is_new:
                        service_log_entry.emails_saved_n += 1
                        email_job_data = self.extract_email_data(email_record, service_log_entry)
                        jobs_data[email_record.platform].update(email_job_data)
                    else:
                        service_log_entry.emails_skipped_n += 1
                        self.logger.info("Email already exists in database. Skipping email.")

                except Exception as exception:
                    message = f"Failed to get and save email data due to error: {exception}. Skipping email."
                    self.logger.exception(message)
                    continue  # next email

        return jobs_data

    def extract_email_data(
        self,
        email_record: JobAlertEmail,
        service_log_entry: EisServiceLog,
    ) -> dict[str, JobResult]:
        """Extract job ids from an email and save them to the database.
        May also extract job data directly from the email for some platforms depending on settings.
        :param email_record: JobAlertEmail record
        :param service_log_entry: Service log entry
        :return: Dictionary of jobs data if the job data were directly extracted from the email"""

        jobs_data = {}

        # LinkedIn
        if email_record.platform == "linkedin":
            job_ids = extract_linkedin_job_ids(email_record.body)
            service_log_entry.linkedin_job_n += len(job_ids)

        # Indeed
        elif email_record.platform == "indeed":

            # Use the email body to extract the job information instead of using the Bright API
            if self.indeed_brightapi_setting == "email":
                jobs = extract_indeed_jobs_from_email(email_record.body)

                # From each job, extract the job ID and add it to the dictionary
                for job in jobs:
                    try:
                        job_id = extract_indeed_job_ids(job.job.url)[0]
                        jobs_data[job_id] = job
                    except Exception as exception:
                        message = (
                            f"Failed to extract job ID from email body for job URL {job.job.url} "
                            f"due to error: {exception}. Skipping job."
                        )
                        self.logger.exception(message)
                        continue  # next job
                job_ids = list(jobs_data.keys())

            # Using BrightAPI
            else:
                job_ids = extract_indeed_job_ids(email_record.body)

            service_log_entry.indeed_job_n += len(job_ids)

        # VeganJobs
        elif email_record.platform == "veganjobs":
            job_ids = extract_veganjobs_job_ids(email_record.body)
            service_log_entry.veganjobs_job_n += len(job_ids)

        else:
            self.logger.info(f"No job IDs found in email: {email_record.external_email_id}. Skipping email.")
            return jobs_data

        email_record.job_found_n = len(job_ids)
        self.db.commit()

        # Save the extracted job ids to the database
        try:
            self.save_job_base_info_to_db(email_record, job_ids)
            service_log_entry.jobs_extracted_n += len(job_ids)
            self.logger.info(f"Extracted and saved {len(job_ids)} job IDs from {email_record.platform}")
        except Exception as exception:
            message = f"Failed to save job IDs for email ID {email_record.external_email_id} due to error: {exception}. Skipping email."
            self.logger.exception(message)

        return jobs_data

    def scrape_jobs(
        self,
        service_log_entry: EisServiceLog,
        jobs_data: dict[str, dict[str, JobResult]],
    ) -> None:
        """Scrape all unscraped jobs
        :param service_log_entry: Service log entry
        :param jobs_data: Dictionary of jobs data extracted from the email content"""

        # List all unique job records that haven't been scraped yet
        job_records = self.db.query(ScrapedJob).filter(ScrapedJob.is_scraped.is_(False)).all()
        service_log_entry.job_total_n = len(job_records)
        self.db.commit()

        # For each job record, scrape the data
        for job_record in job_records:

            # Find any existing scraped job data in the database
            existing_data = (
                self.db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_record.external_job_id)
                .filter(ScrapedJob.is_scraped)
                .first()
            )

            # If previously scraped data exists, copy it to the unscraped record
            if existing_data:
                self.logger.info(
                    f"Job ID {job_record.external_job_id} already has scraped data in the database. "
                    f"Copying data to unscraped record."
                )
                self.copy_existing_entry(existing_data, job_record)

            # Otherwise, scrape the data from the web
            else:
                if job_record.platform == "linkedin":
                    scraper = LinkedinBrightdataJobScraper(job_record.external_job_id)
                elif job_record.platform == "indeed":
                    if self.indeed_brightapi_setting == "email":
                        scraper = None
                    else:
                        scraper = IndeedBrightdataJobScraper(job_record.external_job_id)
                elif job_record.platform == "veganjobs":
                    scraper = VeganJobsJobScraper(job_record.external_job_id)
                else:
                    self.logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                    continue  # next job record

                # Scrape the data and save them to the database
                self.logger.info(f"Scraping job ID: {job_record.external_job_id}")
                try:
                    if scraper is not None:
                        job_data = scraper.scrape_job()[0]
                    else:
                        if job_record.external_job_id not in jobs_data[job_record.platform]:
                            raise ValueError(
                                f"Job data not found in email content for job ID {job_record.external_job_id}"
                            )
                        job_data = jobs_data[job_record.platform][job_record.external_job_id]
                    self.update_scraped_job_data(job_record, job_data)
                    service_log_entry.job_success_n += 1
                except:
                    message = (
                        f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: "
                        f"{traceback.format_exc()}. Skipping job."
                    )
                    self.logger.exception(message)
                    job_record.is_scraped = True
                    job_record.is_failed = True
                    job_record.scrape_error = f"{traceback.format_exc()}"
                    self.db.commit()
                    service_log_entry.job_fail_n += 1


class EmailScraperService:
    """Service wrapper for JobScraper with start/stop functionality"""

    def __init__(self) -> None:
        """Initialise the service with a JobScraper instance."""

        self.scraper = JobEmailScraper()
        self.thread = None
        self.stop_event = threading.Event()
        self.period_hours = 3.0
        self.timedelta_days = 1
        self.thread_status = "stopped"
        self.scraper_running = False
        self.sleep_until = None
        self.sleep_start = None

    def start(self, period_hours: float = 3.0, timedelta_days: int = 1) -> None:
        """Start the scraping service
        :param period_hours: Hours between each scraping run
        :param timedelta_days: Number of days to search for emails"""

        if self.thread_status in ("started", "starting", "stopping"):
            return
        self.thread_status = "starting"

        # Store parameters
        self.period_hours = period_hours
        self.timedelta_days = timedelta_days

        # Clear the stop event
        self.stop_event.clear()

        # Start the service in a separate thread
        self.thread = threading.Thread(target=self._run_service, args=(period_hours, timedelta_days))
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        """Stop the scraping service"""

        if self.thread_status in ("stopped", "starting", "stopping"):
            return
        self.thread_status = "stopping"

        self.stop_event.set()

    def _run_service(self, period_hours: float, timedelta_days: int) -> None:
        """Internal method that runs the scraping loop
        :param period_hours: Hours between each scraping run
        :param timedelta_days: Number of days to search for emails"""

        try:
            self.thread_status = "started"
            while not self.stop_event.is_set():
                try:
                    # Run the scraping
                    self.scraper_running = True
                    result = self.scraper.run_scraping(timedelta_days=timedelta_days)
                    self.scraper_running = False

                    duration = result.run_duration
                    sleep_time = max([0, period_hours * 3600 - duration])

                    # Track sleep timing
                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + sleep_time

                    if self.stop_event.wait(timeout=sleep_time):
                        break

                    # Clear sleep tracking after waking
                    self.sleep_start = None
                    self.sleep_until = None

                except Exception:
                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + 300

                    if self.stop_event.wait(timeout=300):  # 5 minutes
                        break

                    self.sleep_start = None
                    self.sleep_until = None
        finally:
            self.thread_status = "stopped"
            self.sleep_start = None
            self.sleep_until = None

    def status(self) -> dict:
        """Get the current status of the service"""

        return {
            "thread_status": self.thread_status,
            "scraper_running": self.scraper_running,
            "period_hours": self.period_hours,
            "timedelta_days": self.timedelta_days,
            "sleep_until": self.sleep_until,
        }
