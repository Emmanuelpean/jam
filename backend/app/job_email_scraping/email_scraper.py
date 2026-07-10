"""Email scraper service.

Reads job alert emails from a shared inbox, extracts job IDs for supported
platforms (LinkedIn, Indeed, Veganjobs, etc.), stores email and job metadata in the
database, scrapes full job details (via platform scrapers or from email
content), and records run statistics in an JobScrapingServiceLog."""

import datetime as dt
from enum import Enum

from sqlalchemy.orm import Session

from app import models
from app.base_models import ProcessingStatus
from app.config import settings
from app.database import db_session
from app.emails.email_service import EmailService
from app.geolocation.geolocation import geocode_location
from app.job_email_scraping.email_parsers import JOB_PARSERS, ALERT_NAME_EXTRACTORS, PLATFORM_SENDER_EMAILS
from app.job_email_scraping.email_parsers.utils import Platform, remove_style_tags
from app.job_email_scraping.filtering import is_job_filtered_out
from app.job_email_scraping.gmail import extract_forwarding_confirmation_link, extract_gmail_originator
from app.job_email_scraping.job_scrapers import SCRAPERS
from app.job_email_scraping.location_parser import parse_location
from app.job_email_scraping.models import (
    JobEmail,
    ScrapedJob,
    JobEmailScrapingServiceLog,
    JobEmailScrapingPlatformStat,
)
from app.job_email_scraping.schemas import JobResult, JobEmailScrapingServiceLogOut
from app.resources import CURRENCIES
from app.service.models import ServiceErrorLevel, record_error
from app.service.registry import register_service
from app.service.service import BaseService


class EmailProvider(Enum):
    """Enum of email providers"""

    GMAIL = "gmail"


FORWARDING_EMAILS = {EmailProvider.GMAIL: "forwarding-noreply@google.com"}
FORWARDING_LINK_EXTRACTORS = {EmailProvider.GMAIL: extract_forwarding_confirmation_link}
ORIGINATOR_EXTRACTORS = {EmailProvider.GMAIL: extract_gmail_originator}


class JobEmailScrapingService(EmailService, BaseService[JobEmailScrapingServiceLog]):
    """Job Email Alert Scraper"""

    service_name = "email_scraper_service"

    def __init__(self) -> None:
        """Object constructor"""

        EmailService.__init__(self, settings.scraper_email_username, settings.scraper_email_password)
        BaseService.__init__(self, JobEmailScrapingServiceLog)

    @staticmethod
    def upsert_platform_stat(
        db: Session,
        service_log: JobEmailScrapingServiceLog,
        platform: Platform,
        **kwargs,
    ) -> JobEmailScrapingPlatformStat:
        """Create a new platform statistics entry
        :param db: Database session
        :param service_log: associated JobEmailScrapingServiceLog instance
        :param platform: Platform enum value
        :param kwargs: PlatformStat keyword arguments"""

        # Check the platform_stats entry exists
        platform_stats = (
            db.query(JobEmailScrapingPlatformStat)
            .join(JobEmailScrapingServiceLog)
            .filter(JobEmailScrapingServiceLog.id == service_log.id)
            .filter(JobEmailScrapingPlatformStat.name == platform)
            .first()
        )

        # Update existing entry by adding the new values
        if not platform_stats:
            platform_stats = JobEmailScrapingPlatformStat(service_log_id=service_log.id, name=platform)
            db.add(platform_stats)

        for key in kwargs:
            if isinstance(kwargs[key], list):
                value = kwargs[key]
            else:
                value = [kwargs[key]]
            setattr(platform_stats, key, list(set(getattr(platform_stats, key) + value)))

        db.commit()
        db.refresh(platform_stats)
        return platform_stats

    @staticmethod
    def is_user_over_monthly_quota(
        db: Session,
        owner_id: int,
    ) -> bool:
        """Check if a user has exceeded their monthly scrape quota.
        :param db: Database session
        :param owner_id: User ID
        :return: True if the user has exceeded their quota"""

        start_of_month = dt.datetime.now(dt.timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        count = (
            db.query(ScrapedJob)
            .filter(ScrapedJob.owner_id == owner_id)
            .filter(ScrapedJob.status == ProcessingStatus.COMPLETED)
            .filter(ScrapedJob.scrape_datetime >= start_of_month)
            .count()
        )
        return count >= settings.monthly_scrape_quota

    def extract_forwarding_email_confirmation(
        self,
        db: Session,
        service_log: JobEmailScrapingServiceLog,
        timedelta_days: int | float = 1,
    ) -> None:
        """Extract and save forwarding confirmation links from emails sent by different email providers
        :param db: Database session
        :param service_log: associated JobEmailScrapingServiceLog instance
        :param timedelta_days: Number of days to search for emails"""

        for email_platform in EmailProvider:
            try:
                email = FORWARDING_EMAILS[email_platform]
                email_ids = self.get_email_ids(from_email=email, timedelta_days=timedelta_days)
            except Exception as exc:
                message = f"Failed to get forwarding emails with platform {email_platform.value}."
                record_error(db, exc, message=message, job_email_scraping_service_log_id=service_log.id)
                self.logger.exception(message)
                continue

            for email_id in email_ids:
                # Try to save the email if it does not already exist
                try:
                    existing_entry = (
                        db.query(models.ForwardingConfirmationLink)
                        .filter(models.ForwardingConfirmationLink.email_external_id == email_id)
                        .first()
                    )
                    if existing_entry:
                        self.logger.info(f"Forwarding confirmation link for email {email_id} already exists. Skipping.")
                        continue
                    else:
                        email = self.get_email_data(email_id)
                except Exception as exc:
                    message = f"Failed to read forwarding email {email_id} with platform {email_platform}."
                    record_error(db, exc, message=message, job_email_scraping_service_log_id=service_log.id)
                    self.logger.exception(message)
                    continue

                try:
                    # Extract the forwarding link
                    link = FORWARDING_LINK_EXTRACTORS[email_platform](email.body)
                    if not link:
                        message = "Forwarding confirmation link not found in email body. Skipping email."
                        self.logger.warning(message)
                        continue

                    # Extract the user email and user details
                    user_email = ORIGINATOR_EXTRACTORS[email_platform](email.body)
                    user = db.query(models.User).filter(models.User.email == user_email).first()
                    if not user:
                        message = f"User with email {user_email} not found in database. Skipping email."
                        self.logger.warning(message)
                        continue

                    # Create the confirmation email
                    confirmation = models.ForwardingConfirmationLink(
                        email_external_id=email.id,
                        url=link,
                        platform=email_platform.value,
                        owner_id=user.id,
                    )
                    db.add(confirmation)
                    db.commit()
                except Exception as exc:
                    message = f"Failed to extract forwarding confirmation link from email {email.id}"
                    record_error(db, exc, message=message, job_email_scraping_service_log_id=service_log.id)
                    self.logger.exception(message)

    # ------------------------------------------------ EMAIL PROCESSING ------------------------------------------------

    def get_and_save_email_to_db(
        self,
        db: Session,
        email_id: str,
        user: models.User,
        service_log_id: int,
        forwarded: bool = False,
    ) -> tuple[JobEmail | None, bool]:
        """Read and save an email to the database
        :param db: Database session
        :param email_id: Email ID
        :param user: User entry associated with this email
        :param service_log_id: ID of the JobEmailScrapingServiceLog instance associated with this email
        :param forwarded: Whether the email was forwarded
        :return: JobEmails instance and whether the record was created or already existing"""

        # Check if the email already exists and return it if it does
        existing_email = db.query(JobEmail).filter(JobEmail.external_email_id == email_id).first()

        # Return the existing email
        if existing_email:
            return existing_email, False

        else:

            # Read the email content and determine the platform
            message = self.get_email_data(email_id)

            # Determine the platform
            platform = PLATFORM_SENDER_EMAILS.get(message.from_email.lower())
            if not platform:
                for plat in PLATFORM_SENDER_EMAILS:
                    if plat in message.body.lower():
                        platform = PLATFORM_SENDER_EMAILS[plat]
                        break
            if not platform:
                self.logger.info(f"Email with ID {email_id} does not have a valid platform.")
                return None, True
            alert_name = ALERT_NAME_EXTRACTORS[platform](message.subject, message.body)
            sender = message.from_email if forwarded else message.to_email

            # Create a new email record
            email_record = JobEmail(
                owner_id=user.id,
                service_log_id=service_log_id,
                external_email_id=email_id,
                subject=message.subject,
                sender=sender,
                date_received=message.date,
                body=remove_style_tags(message.body),
                platform=platform,
                alert_name=alert_name,
            )
            db.add(email_record)
            db.commit()
            db.refresh(email_record)

            return email_record, True

    # ------------------------------------------------- JOB PROCESSING -------------------------------------------------

    def process_job_result(self, db: Session, job_result: JobResult) -> dict:
        """Process a single JobResult and extract relevant data
        :param db: Database session
        :param job_result: JobResult instance
        :return dictionary of extracted job data"""

        result = {}  # noqa

        # Location & attendance type
        result["raw_location"] = job_result.location
        result["location"], result["attendance_type"] = parse_location(result["raw_location"])

        if result["location"]:
            geolocation = geocode_location(result["location"], db, self.logger)
            if geolocation:
                result["geolocation_id"] = geolocation.id

        # Salary
        result["salary_min"] = job_result.job.salary.min_amount
        result["salary_max"] = job_result.job.salary.max_amount
        result["salary_currency"] = None
        currency_code = (job_result.job.salary.currency or "").lower()
        for currency in CURRENCIES:
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
        result["is_closed"] = job_result.job.is_closed

        return result

    def save_job_base_info_to_db(
        self,
        db: Session,
        email_record: JobEmail,
        job_results: list[JobResult],
    ) -> list[ScrapedJob]:
        """Save extracted job IDs from an email to the database and link them to the email.
        If they already exist, just link them to the email.
        :param db: Database session
        :param email_record: associated JobAlertEmail record instance
        :param job_results: list of job IDs to save
        :return: list of ScrapedJob instances created or already existing in the database"""

        job_records = []

        for job_result in job_results:

            # Check if the job already exists for this owner
            existing_entry = (
                db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_result.job_id)
                .filter(ScrapedJob.owner_id == email_record.owner_id)
                .first()
            )

            # Create new job record if it doesn't exist
            if not existing_entry:
                data = self.process_job_result(db, job_result)

                new_job = ScrapedJob(
                    owner_id=email_record.owner_id,
                    service_log_id=email_record.service_log_id,
                    **data,
                )
                new_job.emails.append(email_record)
                db.add(new_job)
                job_records.append(new_job)

            # Link existing job record to the email
            else:
                # Check if this email is already linked to avoid duplicates
                if email_record not in existing_entry.emails:
                    existing_entry.emails.append(email_record)
                job_records.append(existing_entry)

        # Commit and refresh the records
        db.commit()
        for job_record in job_records:
            db.refresh(job_record)

        return job_records

    def update_scraped_job_data(
        self,
        db: Session,
        job_record: ScrapedJob,
        job_result: JobResult | None,
    ) -> None:
        """Update the job records with the scraped data
        :param db: Database session
        :param job_record: ScrapedJob instance
        :param job_result: scraped job data"""

        # Update the job data
        if job_result is not None:
            data = self.process_job_result(db, job_result)
            for key in data:
                if data[key] is not None:
                    setattr(job_record, key, data[key])

        # Scraping succeeded: record the timestamp and mark the job COMPLETED.
        job_record.scrape_datetime = dt.datetime.now()
        job_record.status = ProcessingStatus.COMPLETED

        db.commit()

    @staticmethod
    def copy_existing_entry(
        db: Session,
        job_record1: ScrapedJob,
        job_record2: ScrapedJob,
    ) -> ScrapedJob:
        """Copy the data from job_record1 to job_record2
        :param db: Database session
        :param job_record1: Source ScrapedJob instance
        :param job_record2: Target ScrapedJob instance
        :return: Updated job_record2 instance"""

        columns = [
            "scrape_datetime",
            "title",
            "description",
            "salary_min",
            "salary_max",
            "salary_currency",
            "url",
            "deadline",
            "company",
            "is_closed",
            "raw_location",
            "location",
            "attendance_type",
        ]
        for key in columns:
            if getattr(job_record2, key) is not None:
                setattr(job_record2, key, getattr(job_record1, key))
        db.commit()
        return job_record2

    # ----------------------------------------------------- RUNNER -----------------------------------------------------

    @staticmethod
    def compute_lookback_days(
        db: Session,
        service_log: JobEmailScrapingServiceLog,
        min_timedelta_days: int | float,
        max_timedelta_days: int | float,
    ) -> float | int:
        """Compute the email lookback window from the gap since the previous run.
        Returns the number of days elapsed since the most recent prior run, clamped to
        [min_timedelta_days, max_timedelta_days]. Uses max_timedelta_days on the first run
        (no prior run). Basing the window on the actual gap means a scheduler that was down for a few
        days automatically looks further back to catch up, without replaying weeks of old emails.
        :param db: Database session
        :param service_log: The current run's service log (excluded from the lookup)
        :param min_timedelta_days: Lower bound for the lookback window, in days
        :param max_timedelta_days: Upper bound for the lookback window, in days
        :return: The lookback window in days"""

        last_run = (
            db.query(JobEmailScrapingServiceLog)
            .filter(JobEmailScrapingServiceLog.id != service_log.id)
            .filter(JobEmailScrapingServiceLog.is_tour.is_(False))
            .order_by(JobEmailScrapingServiceLog.run_datetime.desc(), JobEmailScrapingServiceLog.id.desc())
            .first()
        )
        if last_run is None:
            return max_timedelta_days

        elapsed_days = (service_log.run_datetime - last_run.run_datetime).total_seconds() / 86400
        return max(min_timedelta_days, min(max_timedelta_days, elapsed_days))

    def run(
        self,
        min_timedelta_days: int | float = 1,
        max_timedelta_days: int | float = 10,
    ) -> JobEmailScrapingServiceLog:
        """Run the email scraping workflow.
        The email lookback window is derived from the gap since the previous run, clamped to
        [min_timedelta_days, max_timedelta_days].
        :param min_timedelta_days: Minimum number of days to search for emails
        :param max_timedelta_days: Maximum number of days to search for emails"""

        with db_session() as db:
            service_log = self.start_run(db)
            timedelta_days = self.compute_lookback_days(db, service_log, min_timedelta_days, max_timedelta_days)
            self.logger.info(f"Using an email lookback window of {timedelta_days:.2f} day(s)")
            self.extract_forwarding_email_confirmation(db, service_log, timedelta_days)

            try:
                self.process_emails(db, timedelta_days, service_log)
                self.scrape_jobs(db, service_log)
            except Exception as exception:
                message = "Critical error in scraping workflow."
                self.logger.exception(message)
                record_error(
                    db,
                    exception,
                    message=message,
                    job_email_scraping_service_log_id=service_log.id,
                    level=ServiceErrorLevel.CRITICAL,
                )
            finally:
                service_log.set_run_duration()
                self.logger.info("Finished email scraping workflow")

            db.commit()
            return service_log

    def process_emails(
        self,
        db: Session,
        timedelta_days: int | float,
        service_log: JobEmailScrapingServiceLog,
    ) -> None:
        """For each user, get and save each new email, then extract the job ids and job data.
        :param db: Database session
        :param timedelta_days: Number of days to search for emails
        :param service_log: JobEmailScrapingServiceLog entry"""

        # Get the list of active users with TOAST active
        users = (
            db.query(models.User)
            .filter(models.User.premium.has(is_active=True, job_scraping_active=True))
            .filter(models.User.is_active)
            .filter(models.User.is_verified)
            .all()
        )
        self.logger.info(f"Found {len(users)} users to process.")
        service_log.user_found_ids = [user.id for user in users]

        # For each user...
        for user in users:
            self.logger.info(f"Processing user: {user.email} (ID: {user.id})")

            # Get the list of all emails
            forwarded = False
            try:
                email_ids = self.get_email_ids(
                    recipient_email=settings.scraper_email_username,
                    sender_email=user.email,
                    timedelta_days=timedelta_days,
                    from_email=list(PLATFORM_SENDER_EMAILS.keys()),
                )
                # If no emails found, look for forwarded emails
                if not email_ids:
                    email_ids = self.get_email_ids(
                        from_email=user.email,
                        to_email=settings.scraper_email_username,
                        timedelta_days=timedelta_days,
                    )
                    forwarded = True
                service_log.email_found_n += len(email_ids)
                self.logger.info(f"Found {len(email_ids)} emails")
            except Exception as exception:
                message = f"Failed to search emails for user ID {user.id}"
                record_error(db, exception, message, job_email_scraping_service_log_id=service_log.id)
                self.logger.exception(f"{message}. Skipping user.")
                email_ids = []

            # For each email...
            for email_id in email_ids:
                self.logger.info(f"Processing email with ID: {email_id}")
                try:
                    email_record, is_new = self.get_and_save_email_to_db(db, email_id, user, service_log.id, forwarded)

                    if not email_record:
                        continue

                    # Extract jobs if this is a new email
                    email_kwargs = dict(db=db, service_log=service_log, platform=email_record.platform)
                    if is_new:
                        self.upsert_platform_stat(email_saved_ids=email_record.id, **email_kwargs)
                        self.extract_email_data(db, email_record, service_log)
                    else:
                        self.upsert_platform_stat(email_skipped_ids=email_record.id, **email_kwargs)
                        self.logger.info("Email already exists in database. Skipping email.")

                except Exception as exception:
                    message = f"Failed to get and save email with ID {email_id}"
                    record_error(db, exception, message, job_email_scraping_service_log_id=service_log.id)
                    self.logger.exception(f"{message}. Skipping email.")
                    continue  # next email

            # noinspection PyAugmentAssignment
            service_log.user_processed_ids = service_log.user_processed_ids + [user.id]

    def extract_email_data(
        self,
        db: Session,
        email_record: JobEmail,
        service_log: JobEmailScrapingServiceLog,
    ) -> None:
        """Extract job ids from an email and save them to the database.
        May also extract job data directly from the email for some platforms depending on settings.
        :param db: Database session
        :param email_record: JobEmail record
        :param service_log: Service log entry
        :return: Dictionary of jobs data if the job data were directly extracted from the email"""

        try:
            jobs = JOB_PARSERS[email_record.platform](email_record.body)
        except Exception as exception:
            message = f"Failed to parse email ID {email_record.external_email_id}"
            record_error(db, exception, message, job_email_scraping_service_log_id=service_log.id)
            self.logger.exception(f"{message}. Skipping email.")
            return None  # skip the email parsing

        # Update the email record with the number of jobs found
        email_record.job_found_n = len(jobs)
        db.commit()

        # Save the extracted job ids to the database
        try:
            scraped_jobs = self.save_job_base_info_to_db(db, email_record, jobs)
            job_found_ids = [j.id for j in scraped_jobs]
            self.upsert_platform_stat(db, service_log, email_record.platform, job_found_ids=job_found_ids)
            self.logger.info(f"Extracted and saved {len(jobs)} job IDs from {email_record.platform}")
        except Exception as exception:
            message = f"Failed to save job IDs for email ID {email_record.external_email_id}"
            record_error(db, exception, message=message, job_email_scraping_service_log_id=service_log.id)
            self.logger.exception(f"{message}. Skipping email.")

    def scrape_jobs(self, db: Session, service_log: JobEmailScrapingServiceLog) -> None:
        """Process all unscraped jobs, including those scheduled for retry.
        :param db: Database session
        :param service_log: Service log entry"""

        # List all unprocessed job records, including those whose retry window has passed
        job_records = db.query(ScrapedJob).filter(ScrapedJob.is_pending).all()
        platforms = set([job.platform for job in job_records])
        for platform in platforms:
            job_ids = [job.id for job in job_records if job.platform == platform]
            self.upsert_platform_stat(db, service_log, platform, job_to_process_ids=job_ids)

        # For each job record...
        for job_record in job_records:

            # Check if filtered out
            try:
                if job_filter_rule := is_job_filtered_out(db, job_record):
                    self.logger.info(
                        f"Job ID {job_record.external_job_id} filtered out for user ID {job_record.owner_id} "
                        f"due to rule {job_filter_rule.name}"
                    )
                    job_record.status = ProcessingStatus.FILTERED
                    job_record.exclusion_filter_id = job_filter_rule.id
                    db.commit()
                    self.upsert_platform_stat(
                        db, service_log, job_record.platform, job_scrape_filtered_ids=job_record.id
                    )
                    continue  # next job record
            except Exception as exception:
                message = (
                    f"Failed to check filtering for job ID {job_record.external_job_id}. Proceeding with scraping."
                )
                record_error(db, exception, message=message, job_email_scraping_service_log_id=service_log.id)
                self.logger.exception(message)

            # Find any existing successfully scraped job data in the database
            existing_data = (
                db.query(ScrapedJob)
                .filter(ScrapedJob.external_job_id == job_record.external_job_id)
                .filter(ScrapedJob.platform == job_record.platform)
                .filter(ScrapedJob.status == ProcessingStatus.COMPLETED)
                .first()
            )

            # If previously scraped data exists, copy it to the unscraped record
            if existing_data:
                self.logger.info(
                    f"Job ID {job_record.external_job_id} already has scraped data in the database. "
                    f"Copying data to unscraped record."
                )
                self.copy_existing_entry(db, existing_data, job_record)
                job_record.status = ProcessingStatus.COPIED
                db.commit()
                self.upsert_platform_stat(db, service_log, job_record.platform, job_scrape_copied_ids=job_record.id)
                continue  # next job record

            # Check if user has exceeded their monthly scrape quota
            if self.is_user_over_monthly_quota(db, job_record.owner_id):
                self.logger.info(
                    f"User ID {job_record.owner_id} has exceeded their monthly scrape quota of "
                    f"{settings.monthly_scrape_quota}. Skipping job ID {job_record.external_job_id}."
                )
                job_record.status = ProcessingStatus.SKIPPED
                job_record.skip_reason = f"Monthly scrape quota of {settings.monthly_scrape_quota} exceeded"
                db.commit()
                self.upsert_platform_stat(db, service_log, job_record.platform, job_scrape_skipped_ids=job_record.id)
                continue  # next job record

            # Otherwise, scrape the job data
            if job_record.platform in SCRAPERS:
                scraper = SCRAPERS[job_record.platform](job_record.external_job_id)
                self.logger.info(f"Scraping job ID: {job_record.external_job_id}")
                try:
                    job_data = scraper.scrape_job()[0]
                    self.update_scraped_job_data(db, job_record, job_data)
                    job_record.scraping_next_retry_at = None
                    db.commit()
                    self.upsert_platform_stat(
                        db, service_log, job_record.platform, job_scrape_succeeded_ids=job_record.id
                    )
                except Exception as exception:
                    message = f"Failed to scrape job data for job ID {job_record.external_job_id}"
                    record_error(
                        db,
                        exception,
                        message=message,
                        scraped_job_id=job_record.id,
                        job_email_scraping_service_log_id=service_log.id,
                    )
                    self.logger.exception(f"{message}. Skipping job.")
                    job_record.scraping_retry_count += 1
                    if job_record.scraping_retry_count < settings.scrape_max_retry:
                        job_record.scraping_next_retry_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                            hours=settings.scrape_retry_delay_hours
                        )
                        self.logger.info(
                            f"Scheduled retry {job_record.scraping_retry_count}/{settings.scrape_max_retry} for job ID "
                            f"{job_record.external_job_id} in {settings.scrape_retry_delay_hours}h"
                        )
                    else:
                        job_record.status = ProcessingStatus.FAILED
                        self.logger.info(
                            f"Job ID {job_record.external_job_id} permanently failed after "
                            f"{settings.scrape_max_retry} attempts"
                        )
                    db.commit()
                    self.upsert_platform_stat(db, service_log, job_record.platform, job_scrape_failed_ids=job_record.id)
            else:
                message = f"Unknown platform {job_record.platform} for job ID {job_record.external_job_id}"
                self.logger.info(f"{message}. Skipping job.")
                job_record.status = ProcessingStatus.FAILED
                record_error(
                    db,
                    ValueError(f"Unknown platform {job_record.platform}"),
                    message,
                    job_email_scraping_service_log_id=service_log.id,
                )
                db.commit()
                continue  # next job record


register_service(
    JobEmailScrapingService.service_name,
    JobEmailScrapingService().run,
    display_name="Job Email Scraping",
    run_period_hours=3,
    log_model=JobEmailScrapingServiceLog,
    log_schema=JobEmailScrapingServiceLogOut,
    default_parameters={"min_timedelta_days": 1, "max_timedelta_days": 10},
)
