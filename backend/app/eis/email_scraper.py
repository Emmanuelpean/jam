"""Email scraper service.

Reads job alert emails from a shared inbox, extracts job IDs for supported
platforms (linkedin, indeed, veganjobs), stores email and job metadata in the
database, scrapes full job details (via platform scrapers or from email
content), and records run statistics in an EisServiceLog."""

import threading
import traceback
from datetime import datetime

from app import models
from app.config import settings
from app.database import get_db
from app.eis.job_scraper import LinkedinJobScraper, IndeedJobScraper, VeganJobsScraper, extract_indeed_jobs_from_email
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog
from app.emails.email_service import EmailService
from app.utils import AppLogger
from app.eis.email_parser import extract_linkedin_job_ids, extract_indeed_job_ids, extract_veganjobs_job_ids
from app.eis.location_parser import LocationParser

PLATFORMS = ["linkedin", "indeed", "veganjobs"]


class JobScraper(EmailService):
    """Job Scrapper"""

    def __init__(self, db=None) -> None:
        """Object constructor
        :param db: optional database session"""

        EmailService.__init__(self)
        self.location_parser = LocationParser()
        self.logger = AppLogger.create_service_logger("email_scraper", "INFO")
        self.db = next(get_db()) if db is None else db

    @property
    def indeed_brightapi_setting(self):
        """Get the Indeed BrightAPI setting from the database"""

        return models.get_setting(self.db, "indeed_scraper", "email")

    def create_service_log(self, **kwargs) -> EisServiceLog:
        """Create a new service log entry
        :param kwargs: EisServiceLog fields"""

        # noinspection PyArgumentList
        service_log_entry = EisServiceLog(**kwargs)
        self.db.add(service_log_entry)
        self.db.commit()
        self.db.refresh(service_log_entry)
        return service_log_entry

    # ------------------------------------------------- EMAIL READING -------------------------------------------------

    def get_and_save_email_to_db(
        self,
        message_id: str,
        user: models.User,
        service_log_id: int,
    ) -> tuple[JobAlertEmail, bool]:
        """Save email and job IDs to database
        :param message_id: Message ID
        :param user: User entry
        :param service_log_id: ID of the EisServiceLog instance associated with this email
        :return: JobEmails instance and whether the record was created or already existing"""

        # Check if the email already exists and return it if it does
        existing_email = self.db.query(JobAlertEmail).filter(JobAlertEmail.external_email_id == message_id).first()

        # Return the existing email
        if existing_email:
            return existing_email, False

        else:

            # Read the email content and determine the platform
            message = self.get_email_data(message_id)

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
                external_email_id=message_id,
                subject=message["subject"],
                sender=message["to"],
                date_received=message["date"],
                body=message["body"],
                platform=platform,
            )  # noqa
            self.db.add(email_record)
            self.db.commit()
            self.db.refresh(email_record)

            # Delete the email from the inbox after saving to DB
            # self.delete_email(message_id)  # TODO to uncomment

            return email_record, True

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    def save_job_base_info_to_db(
        self,
        email_record: JobAlertEmail,
        job_ids: list[str],
    ) -> list[ScrapedJob]:
        """Save extracted job IDs to the database and link them to the email for the email owner.
        If they already exist, just link them.
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

            if not existing_entry:
                # Create new job record
                new_job = ScrapedJob(external_job_id=job_id, owner_id=email_record.owner_id)  # noqa
                new_job.emails.append(email_record)
                self.db.add(new_job)
                job_records.append(new_job)

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
        job_data: dict,
    ) -> None:
        """Update the job records with the scraped data
        :param job_record: ScrapedJob instance
        :param job_data: scraped job data"""

        location, attendance_type = self.location_parser.parse_location(job_data["location"])
        job_record.company = job_data["company"]
        job_record.location_postcode = location.postcode
        job_record.location_city = location.city
        job_record.location_country = location.country
        job_record.attendance_type = attendance_type
        job_record.salary_min = job_data["job"]["salary"]["min_amount"]
        job_record.salary_max = job_data["job"]["salary"]["max_amount"]
        job_record.title = job_data["job"]["title"]
        job_record.description = job_data["job"]["description"]
        job_record.url = job_data["job"]["url"]
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
            self.scrape_save_jobs(service_log, jobs_data)

            # Log final statistics
            service_log.run_duration = (datetime.now() - start_time).total_seconds()
            success = True
            error_message = None

        except Exception as exception:
            self.logger.exception(f"Critical error in scraping workflow: {exception}")
            service_log.run_duration = (datetime.now() - start_time).total_seconds()
            success = False
            error_message = str(exception)

        service_log.is_success = success
        service_log.error_message = error_message
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
        self.logger.info(f"Found {len(users)} users to process")
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
    ) -> dict[str, dict]:
        """Extract job ids from an email and save them to the database
        :param email_record: JobAlertEmail record
        :param service_log_entry: Service log entry
        :return: Dictionary of jobs data if the job data were directly extracted from the email"""

        jobs_data = {}

        # LinkedIn jobs
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
                        job_id = extract_indeed_job_ids(job["job"]["url"])[0]
                        jobs_data[job_id] = job
                    except Exception as exception:
                        message = (
                            f"Failed to extract job ID from email body for job URL {job['job']['url']} "
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
            self.logger.info(f"No job IDs found in email: {email_record.email_external_id}. Skipping email.")
            return jobs_data

        email_record.job_found_n = len(job_ids)
        self.db.commit()

        # Save the extracted job ids to the database
        try:
            self.save_job_base_info_to_db(email_record, job_ids)
            service_log_entry.jobs_extracted_n += len(job_ids)
            self.logger.info(f"Extracted and saved {len(job_ids)} job IDs from {email_record.platform}")
        except Exception as exception:
            message = f"Failed to save job IDs for email ID {email_record.email_external_id} due to error: {exception}. Skipping email."
            self.logger.exception(message)
            return jobs_data

        return jobs_data

    def scrape_save_jobs(
        self,
        service_log_entry: EisServiceLog,
        jobs_data: dict,
    ) -> None:
        """Scrape all remaining unscraped jobs
        :param service_log_entry: Service log entry
        :param jobs_data: Dictionary of jobs data"""

        # List all unique job records that haven't been scraped yet
        job_records = (
            self.db.query(ScrapedJob)
            .filter(ScrapedJob.is_scraped.is_(False))
            .distinct(ScrapedJob.external_job_id)
            .all()
        )

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
                if job_record.emails[0].platform == "linkedin":
                    scrapper = LinkedinJobScraper(job_record.external_job_id)
                elif job_record.emails[0].platform == "indeed":
                    if self.indeed_brightapi_setting == "email":
                        scrapper = None
                    else:
                        scrapper = IndeedJobScraper(job_record.external_job_id)
                elif job_record.emails[0].platform == "veganjobs":
                    scrapper = VeganJobsScraper(job_record.external_job_id)
                else:
                    self.logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                    continue  # next job record

                # Scrape the data and save them to the database
                self.logger.info(f"Scraping job ID: {job_record.external_job_id}")
                try:
                    if scrapper is not None:
                        job_data = scrapper.scrape_job()[0]
                    else:
                        job_data = jobs_data[job_record.emails[0].platform][job_record.external_job_id]
                    self.update_scraped_job_data(job_record, job_data)
                    service_log_entry.job_success_n += 1
                except:
                    message = f"Failed to scrape job data for job ID {job_record.external_job_id} due to error: {traceback.format_exc()}. Skipping job."
                    self.logger.exception(message)
                    job_record.is_scraped = True
                    job_record.is_failed = True
                    job_record.scrape_error = f"{traceback.format_exc()}"
                    self.db.commit()
                    service_log_entry.job_fail_n += 1


class JobScraperService:
    """Service wrapper for JobScraper with start/stop functionality"""

    def __init__(self) -> None:
        """Initialise the service with a JobScraper instance."""

        self.scraper = JobScraper()
        self.is_running = False
        self.thread = None
        self.stop_event = threading.Event()

    def start(self, period_hours: float = 3.0) -> None:
        """Start the scraping service
        :param period_hours: Hours between each scraping run"""

        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()

        # Start the service in a separate thread
        self.thread = threading.Thread(target=self._run_service, args=(period_hours,))
        self.thread.daemon = False
        self.thread.start()

    def stop(self) -> None:
        """Stop the scraping service"""

        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()

        if self.thread:
            while self.thread.is_alive():
                self.thread.join(timeout=5)  # Wait up to 5 seconds for clean shutdown

    def _run_service(self, period_hours: float) -> None:
        """Internal method that runs the scraping loop
        :param period_hours: Hours between each scraping run"""

        while self.is_running and not self.stop_event.is_set():
            try:

                # Run the scraping
                result = self.scraper.run_scraping(timedelta_days=2)

                duration = result.get("duration_seconds", 0)
                sleep_time = max([0, period_hours * 3600 - duration])
                if self.stop_event.wait(timeout=sleep_time):
                    break

            except Exception:
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


email_scraper = JobScraper()
# emails = email_scraper.get_email_ids(
#     "jam.jobscraper@emmanuelpean.me", "emmanuelpean@gmail.com", inbox_only=True, timedelta_days=1
# )
# email_d = email_scraper.get_email_data(emails[2], "")
# print(emails)
# # print(email_d)
# # scraper.save_email_to_db(email_d, next(get_db()))
# email_scraper.run_scraping(1)
#
#
# @patch("app.config.settings.test_mode", True)
# def test_run():
#     """Test the email scraper"""
#
#     email_scraper = JobScraper()
#     email_scraper.run_scraping(timedelta_days=1)
