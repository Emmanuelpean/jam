"""Email scraper service.

Reads job alert emails from a shared inbox, extracts job IDs for supported
platforms (linkedin, indeed, veganjobs), stores email and job metadata in the
database, scrapes full job details (via platform scrapers or from email
content), and records run statistics in an EisServiceLog."""

import threading
import time
import traceback
from datetime import datetime

from app import models, utils
from app.config import settings
from app.database import get_db
from app.eis.email_parsers.utils import Platform, remove_style_tags
from app.eis.email_parsers import JOB_PARSERS, ALERT_NAME_EXTRACTORS, PLATFORM_SENDER_EMAILS
from app.eis.job_scrapers import JobResult
from app.eis.job_scrapers.indeed import IndeedBrightdataJobScraper
from app.eis.job_scrapers.linkedin import LinkedinBrightdataJobScraper
from app.eis.job_scrapers.nhs import NhsJobScraper
from app.eis.job_scrapers.veganjobs import VeganJobsJobScraper
from app.eis.location_parser import LocationParser
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog, PlatformStat, EisServiceError
from app.emails.email_service import EmailService
from app.utils import AppLogger


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

    def upsert_platform_stat(
        self,
        service_log: EisServiceLog,
        platform: Platform,
        **kwargs,
    ) -> PlatformStat:
        """Create a new platform statistics entry
        :param service_log: associated EisServiceLog instance
        :param platform: Platform enum value
        :param kwargs: PlatformStat keyword arguments"""

        # Check the platform_stats entry exists
        platform_stats = (
            self.db.query(PlatformStat)
            .join(EisServiceLog)
            .filter(EisServiceLog.id == service_log.id)
            .filter(PlatformStat.name == platform)
            .first()
        )

        # Update existing entry by adding the new values
        if not platform_stats:
            platform_stats = PlatformStat(service_log_id=service_log.id, name=platform)
            self.db.add(platform_stats)

        for key in kwargs:
            if isinstance(kwargs[key], list):
                value = kwargs[key]
            else:
                value = [kwargs[key]]
            setattr(platform_stats, key, list(set(getattr(platform_stats, key) + value)))

        self.db.commit()
        self.db.refresh(platform_stats)
        return platform_stats

    def log_eis_service_error(
        self,
        service_log: EisServiceLog,
        exc: Exception,
    ) -> EisServiceError:
        """Create an EisServiceError for a caught exception.
        :param service_log: associated EisServiceLog instance
        :param exc: the caught exception
        :return: EisServiceError instance"""

        tb = traceback.format_exc()
        # noinspection PyArgumentList
        err = EisServiceError(
            error_type=type(exc).__name__,
            message=str(exc),
            traceback=tb,
            service_log_id=service_log.id,
        )
        self.db.add(err)
        self.db.commit()
        return err

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
            platform = PLATFORM_SENDER_EMAILS.get(message["from"].lower())
            if not platform:
                raise ValueError("Email body does not contain a valid platform identifier.")
            alert_name = ALERT_NAME_EXTRACTORS[platform](message["subject"], message["body"])

            # Create a new email record
            # noinspection PyArgumentList
            email_record = JobAlertEmail(
                owner_id=user.id,
                service_log_id=service_log_id,
                external_email_id=email_id,
                subject=message["subject"],
                sender=message["to"],
                date_received=message["date"],
                body=remove_style_tags(message["body"]),
                platform=platform,
                alert_name=alert_name,
            )
            self.db.add(email_record)
            self.db.commit()
            self.db.refresh(email_record)

            # Delete the email from the inbox after saving to DB
            # self.delete_email(message_id)  # TODO to uncomment

            return email_record, True

    # ------------------------------------------------- JOB PROCESSING -------------------------------------------------

    def process_job_result(self, job_result: JobResult) -> dict:
        """Process a single JobResult and extract relevant data
        :param job_result: JobResult instance
        :return dictionary of extracted job data"""

        result = {}

        # Location & attendance type
        raw_location = job_result.location
        parsed_location, attendance_type = self.location_parser.parse_location(raw_location)
        result["location_postcode"] = parsed_location.postcode
        result["location_city"] = parsed_location.city
        result["attendance_type"] = attendance_type
        result["location_country"] = None
        if parsed_location.country:
            for country in self.countries:
                if parsed_location.country.lower() == country["name"].lower():
                    result["location_country"] = country["name"]
                    break

        # Salary
        result["salary_min"] = job_result.job.salary.min_amount
        result["salary_max"] = job_result.job.salary.max_amount
        result["salary_currency"] = None
        currency_code = (job_result.job.salary.currency or "").lower()
        for currency in self.currencies:
            if currency_code in (currency["code"].lower(), currency["symbol_native"].lower()):
                result["salary_currency"] = currency["code"]
                break

        # Job data
        result["raw_url"] = job_result.job.raw_url
        result["url"] = job_result.job.url
        result["title"] = job_result.job.title
        result["description"] = job_result.job.description
        result["company"] = job_result.company
        result["deadline"] = job_result.job.deadline
        result["external_job_id"] = job_result.job_id
        result["platform"] = job_result.platform

        return result

    def save_job_base_info_to_db(
        self,
        email_record: JobAlertEmail,
        job_results: list[JobResult],
    ) -> list[ScrapedJob]:
        """Save extracted job IDs from an email to the database and link them to the email.
        If they already exist, just link them to the email.
        :param email_record: associated JobAlertEmail record instance
        :param job_results: list of job IDs to save
        :return: list of ScrapedJob instances created or already existing in the database"""

        job_records = []

        for job_result in job_results:

            # Check if the job already exists for this owner
            existing_entry = (
                self.db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_result.job_id)
                .filter(ScrapedJob.owner_id == email_record.owner_id)
                .first()
            )

            # Create new job record if it doesn't exist

            if not existing_entry:
                data = self.process_job_result(job_result)

                # noinspection PyArgumentList
                new_job = ScrapedJob(
                    owner_id=email_record.owner_id,
                    service_log_id=email_record.service_log_id,
                    **data,
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
        job_result: JobResult | None,
    ) -> None:
        """Update the job records with the scraped data
        :param job_record: ScrapedJob instance
        :param job_result: scraped job data"""

        # Update the job data
        if job_result is not None:
            data = self.process_job_result(job_result)
            for key in data:
                if data[key] is not None:
                    setattr(job_record, key, data[key])

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
            "platform",
            "location",
            "location_city",
            "location_country",
            "location_postcode",
            "attendance_type",
            "salary_min",
            "salary_max",
            "salary_currency",
            "title",
            "description",
            "scrape_datetime",
            "is_scraped",
            "is_failed",
            "scrape_error",
            "url",
        ]
        for key in columns:
            if getattr(job_record2, key) is not None:
                setattr(job_record2, key, getattr(job_record1, key))
        self.db.commit()
        return job_record2

    # ----------------------------------------------------- RUNNER -----------------------------------------------------

    def run_scraping(self, timedelta_days: int | float = 1) -> EisServiceLog:
        """Run the email scraping workflow
        :param timedelta_days: Number of days to search for emails"""

        start_time = datetime.now()
        self.logger.info("Starting email scraping workflow")
        service_log = self.create_service_log(run_datetime=start_time)

        try:
            # Process emails for all users
            self.process_emails(timedelta_days, service_log)

            # Scrape remaining jobs that haven't been scraped yet
            self.scrape_jobs(service_log)

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
        service_log: EisServiceLog,
    ) -> None:
        """For each user, get and save each new email, then extract the job ids and job data.
        :param timedelta_days: Number of days to search for emails
        :param service_log: EIS Service log entry"""

        # Get the list of active users with TOAST active
        users = (
            self.db.query(models.User)
            .filter(models.User.toast_active, models.User.is_active, models.User.is_verified)
            .all()
        )
        self.logger.info(f"Found {len(users)} users to process.")
        service_log.user_found_ids = [user.id for user in users]

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
                service_log.email_found_n += len(email_ids)
                self.logger.info(f"Found {len(email_ids)} emails")
            except Exception as exception:
                self.log_eis_service_error(service_log, exception)
                self.logger.exception(f"Failed to search messages due to error: {exception}. Skipping user.")
                continue  # next user

            # For each email...
            for email_id in email_ids:
                self.logger.info(f"Processing email with ID: {email_id}")
                try:
                    email_record, is_new = self.get_and_save_email_to_db(email_id, user, service_log.id)

                    # Extract jobs if this is a new email
                    if is_new:
                        self.upsert_platform_stat(service_log, email_record.platform, email_saved_ids=email_record.id)
                        self.extract_email_data(email_record, service_log)
                    else:
                        self.upsert_platform_stat(service_log, email_record.platform, email_skipped_ids=email_record.id)
                        self.logger.info("Email already exists in database. Skipping email.")

                except Exception as exception:
                    self.log_eis_service_error(service_log, exception)
                    self.logger.exception(
                        f"Failed to get and save email data due to error: {exception}. Skipping email."
                    )
                    continue  # next email

            # noinspection PyAugmentAssignment
            service_log.user_processed_ids = service_log.user_processed_ids + [user.id]

    def extract_email_data(
        self,
        email_record: JobAlertEmail,
        service_log: EisServiceLog,
    ) -> None:
        """Extract job ids from an email and save them to the database.
        May also extract job data directly from the email for some platforms depending on settings.
        :param email_record: JobAlertEmail record
        :param service_log: Service log entry
        :return: Dictionary of jobs data if the job data were directly extracted from the email"""

        try:
            jobs = JOB_PARSERS[email_record.platform](email_record.body)
        except Exception as exception:
            self.log_eis_service_error(service_log, exception)
            self.logger.exception(
                f"Failed to parse email ID {email_record.external_email_id} due to error: {exception}."
                f" Skipping email."
            )
            return None  # skip the email parsing

        # Update the email record with the number of jobs found
        email_record.job_found_n = len(jobs)
        self.db.commit()

        # Save the extracted job ids to the database
        try:
            scraped_jobs = self.save_job_base_info_to_db(email_record, jobs)
            self.upsert_platform_stat(service_log, email_record.platform, job_found_ids=[j.id for j in scraped_jobs])
            self.logger.info(f"Extracted and saved {len(jobs)} job IDs from {email_record.platform}")
        except Exception as exception:
            self.log_eis_service_error(service_log, exception)
            self.logger.exception(
                f"Failed to save job IDs for email ID {email_record.external_email_id} due to error: "
                f"{exception}. Skipping email."
            )

    def scrape_jobs(self, service_log: EisServiceLog) -> None:
        """Scrape all unscraped jobs
        :param service_log: Service log entry"""

        # List all unique job records that haven't been scraped yet
        job_records = self.db.query(ScrapedJob).filter(ScrapedJob.is_scraped.is_(False)).all()

        # For each job record, scrape the data
        for job_record in job_records:

            # Find any existing scraped job data in the database
            existing_data = (
                self.db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_record.external_job_id)
                .filter(ScrapedJob.platform == job_record.platform)
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
                self.upsert_platform_stat(service_log, job_record.platform, job_scrape_copied_ids=job_record.id)

            # Otherwise, scrape the data from the web
            else:
                if job_record.platform == Platform.LINKEDIN:
                    scraper = LinkedinBrightdataJobScraper(job_record.external_job_id)
                elif job_record.platform == Platform.INDEED:
                    if self.indeed_brightapi_setting == "email":
                        scraper = None
                    else:
                        scraper = IndeedBrightdataJobScraper(job_record.external_job_id)
                elif job_record.platform == Platform.VEGANJOBS:
                    scraper = VeganJobsJobScraper(job_record.external_job_id)
                elif job_record.platform == Platform.NHS:
                    scraper = NhsJobScraper(job_record.external_job_id)
                else:
                    self.logger.info(f"Unknown platform for job {job_record.external_job_id}. Skipping job.")
                    continue  # next job record

                # Scrape the data and save them to the database
                self.logger.info(f"Scraping job ID: {job_record.external_job_id}")
                try:
                    if scraper is not None:
                        job_data = scraper.scrape_job()[0]
                        self.update_scraped_job_data(job_record, job_data)
                        self.upsert_platform_stat(
                            service_log, job_record.platform, job_scrape_succeeded_ids=job_record.id
                        )
                    else:
                        self.update_scraped_job_data(job_record, None)
                        self.upsert_platform_stat(
                            service_log, job_record.platform, job_scrape_skipped_ids=job_record.id
                        )

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
                    self.upsert_platform_stat(service_log, job_record.platform, job_scrape_failed_ids=job_record.id)


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
        self.logger = AppLogger.create_service_logger("email_scraper_service", "INFO")
        self.logger.info("EmailScraperService initialized")

    def start(self, period_hours: float = 3.0, timedelta_days: int = 1) -> None:
        """Start the scraping service
        :param period_hours: Hours between each scraping run
        :param timedelta_days: Number of days to search for emails"""

        if self.thread_status in ("started", "starting", "stopping"):
            self.logger.warning(f"Cannot start service - current status: {self.thread_status}")
            return

        self.logger.info(f"Starting email scraper service (period: {period_hours}h, timedelta: {timedelta_days}d)")
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
        self.logger.info("Service thread started successfully")

    def stop(self) -> None:
        """Stop the scraping service"""

        if self.thread_status in ("stopped", "starting", "stopping"):
            self.logger.warning(f"Cannot stop service - current status: {self.thread_status}")
            return

        self.logger.info("Stopping email scraper service")
        self.thread_status = "stopping"
        self.stop_event.set()

    def _run_service(self, period_hours: float, timedelta_days: int) -> None:
        """Internal method that runs the scraping loop
        :param period_hours: Hours between each scraping run
        :param timedelta_days: Number of days to search for emails"""

        try:
            self.thread_status = "started"
            self.logger.info("Service loop started")

            while not self.stop_event.is_set():
                try:
                    # Run the scraping
                    self.logger.info(f"Starting scraping run (timedelta: {timedelta_days}d)")
                    self.scraper_running = True
                    result = self.scraper.run_scraping(timedelta_days=timedelta_days)
                    self.scraper_running = False

                    self.logger.info(f"Scraping completed - duration: {result.run_duration:.2f}s")

                    duration = result.run_duration
                    sleep_time = max([0, period_hours * 3600 - duration])

                    # Track sleep timing
                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + sleep_time

                    self.logger.info(f"Sleeping for {sleep_time:.2f}s until next run")

                    if self.stop_event.wait(timeout=sleep_time):
                        self.logger.info("Stop event received during sleep")
                        break

                    # Clear sleep tracking after waking
                    self.sleep_start = None
                    self.sleep_until = None

                except Exception as e:
                    self.logger.exception(f"Error during scraping run: {e}")
                    self.scraper_running = False

                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + 300

                    self.logger.info("Waiting 5 minutes before retry after error")

                    if self.stop_event.wait(timeout=300):  # 5 minutes
                        self.logger.info("Stop event received during error recovery")
                        break

                    self.sleep_start = None
                    self.sleep_until = None
        finally:
            self.logger.info("Service loop ended")
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


scraper_service = EmailScraperService()
