"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt
import traceback

from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db
from app.job_rating.claude import MODEL as CLAUDE_MODEL, claude_query
from app.job_rating.prompts import create_job_only_prompt, create_system_prompt_with_profile
from app.service_runner.service_runner import ServiceRunner
from app.utilities.logger import AppLogger

SERVICE_NAME = "job_rating_service"


def ensure_length_limit(
    text_describer: str,
    text: str,
    max_length: int,
    logger=None,
) -> tuple[str, str | None]:
    """Ensure that the given text is not longer than the given maximum length.
    :param text_describer: A description of the text, for logging purposes
    :param text: The text to check
    :param max_length: The maximum allowed length
    :param logger: The logger to use for logging
    :return: A tuple containing the truncated text and a note explaining why it was truncated, if any."""

    if not text:
        return text, None
    if len(text) > max_length:
        if logger:
            logger.info(f"Job {text_describer} is too long ({len(text)}.")
        text = text[:max_length] + "..."
        note = f"{text_describer.capitalize()} was truncated as it was too long ({len(text)} characters. Limit is {max_length} characters)"
        return text, note
    else:
        return text, None


def get_rating_active_users(db: Session) -> list[models.User]:
    """Get all active users with job rating active
    :param db: Database session
    :return: List of active users with job rating active"""

    return (
        db.query(models.User)
        .filter(models.User.premium.has(is_active=True, job_rating_active=True))
        .filter(models.User.is_active)
        .filter(models.User.is_verified)
        .all()
    )


def get_user_unrated_scraped_jobs(db: Session, user_id: int) -> list[models.ScrapedJob]:
    """Get all unrated scraped jobs for a given user.
    :param db: Database session
    :param user_id: ID of the user to get jobs for
    :return: List of unrated scraped jobs"""

    # noinspection PyComparisonWithNone
    return (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == user_id)
        .filter(models.ScrapedJob.is_processed.is_(True))
        .filter(models.ScrapedJob.is_scraped.is_(True))
        .filter(models.ScrapedJob.is_failed.is_(False))
        .filter(models.ScrapedJob.job_rating == None)
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.exclusion_filter == None)
        .all()
    )


class ScrapedJobRater:
    """Rates scraped jobs against user qualifications using AI."""

    def __init__(self) -> None:
        """Initialise the job rater."""

        self.logger = AppLogger.create_service_logger(SERVICE_NAME, "INFO")

    def run(self, db: Session | None = None) -> models.JobRatingServiceLog:
        """Score all scraped jobs using AI.
        :param db: Database session
        :return: Job rating service log entry"""

        db = next(get_db()) if db is None else db

        # Create service log entry
        start_time = dt.datetime.now()
        service_log = models.JobRatingServiceLog(run_datetime=start_time)
        db.add(service_log)
        db.commit()
        db.refresh(service_log)

        try:
            # Get all active users with job rating active
            users = get_rating_active_users(db)
            self.logger.info(f"Found {len(users)} active users to process")
            service_log.user_found_ids = [user.id for user in users]

            # Get latest system and job prompt templates
            system_prompt = db.query(models.AiSystemPrompt).order_by(models.AiSystemPrompt.id.desc()).first()
            job_prompt = db.query(models.AiJobPromptTemplate).order_by(models.AiJobPromptTemplate.id.desc()).first()
            if not system_prompt or not job_prompt:
                raise Exception("No system or job prompt templates found")

            # Process each user
            for user in users:
                self._process_user(db, user.id, service_log, system_prompt, job_prompt)

            # Mark service log as successful
            service_log.is_success = True

        except Exception as exception:
            self.logger.exception(f"Critical error in rating workflow: {exception}")
            service_log.is_success = False
            service_log.error_message = str(exception)
        finally:
            self.logger.info("Finished workflow")

        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        db.commit()
        db.refresh(service_log)
        return service_log

    def _process_user(
        self,
        db: Session,
        user_id: int,
        service_log: models.JobRatingServiceLog,
        system_prompt: models.AiSystemPrompt,
        job_prompt_template: models.AiJobPromptTemplate,
    ) -> None:
        """Process a single user's jobs.
        :param db: Database session
        :param user_id: The ID of the user to process jobs for
        :param service_log: Job rating service log entry
        :param system_prompt: Latest system prompt template
        :param job_prompt_template: Latest job prompt template"""

        # Ensure that the user has a qualification
        user_qualification = (
            db.query(models.UserQualification)
            .filter(models.UserQualification.owner_id == user_id)
            .order_by(models.UserQualification.modified_at.desc())
            .first()
        )
        if not user_qualification:
            self.logger.info(f"Skipping user {user_id} as no user qualification found")
            return
        else:
            self.logger.info(f"Processing user {user_id}")
        scraped_jobs = get_user_unrated_scraped_jobs(db, user_id)
        service_log.job_found_ids = service_log.job_found_ids + [job.id for job in scraped_jobs]
        self.logger.info(f"Found {len(scraped_jobs)} scraped jobs to rate")

        # Build the combined system prompt (instructions + candidate profile) once per user
        # so Anthropic caches it across all jobs for this user
        combined_system_prompt = create_system_prompt_with_profile(
            prompt_template=system_prompt.prompt,
            user_experience=user_qualification.experience,
            user_education=user_qualification.education,
            user_skills=user_qualification.skills,
            user_qualities=user_qualification.qualities,
            user_interests=user_qualification.interests,
        )

        for scraped_job in scraped_jobs:
            self._rate_job(
                db,
                scraped_job,
                user_id,
                user_qualification,
                service_log,
                system_prompt,
                job_prompt_template,
                combined_system_prompt,
            )

        service_log.user_processed_ids = service_log.user_processed_ids + [user_id]
        db.commit()

    def _rate_job(
        self,
        db: Session,
        scraped_job: models.ScrapedJob,
        user_id: int,
        user_qualification: models.UserQualification,
        service_log: models.JobRatingServiceLog,
        system_prompt: models.AiSystemPrompt,
        job_prompt_template: models.AiJobPromptTemplate,
        combined_system_prompt: str,
    ) -> None:
        """Rate a single scraped job.
        :param db: Database session
        :param scraped_job: The scraped job to rate
        :param user_id: The ID of the user to rate the job for
        :param user_qualification: The user's qualification
        :param service_log: Job rating service log entry
        :param system_prompt: Latest system prompt template
        :param job_prompt_template: Latest job prompt template
        :param combined_system_prompt: Pre-built system prompt with candidate profile embedded"""

        self.logger.info(f"Processing job ID {scraped_job.id}")
        notes = []

        job_rating_kwargs = dict(
            scraped_job_id=scraped_job.id,
            owner_id=user_id,
            user_qualification_id=user_qualification.id,
            system_prompt_id=system_prompt.id,
            job_prompt_template_id=job_prompt_template.id,
            llm_model=CLAUDE_MODEL,
        )

        # Check that the job is not closed
        if scraped_job.is_closed or (scraped_job.deadline and scraped_job.deadline < dt.datetime.now(dt.timezone.utc)):
            self.logger.info(f"Skipping job ID {scraped_job.id} as it is closed")
            job_rating = models.JobRating(
                is_skipped=True,
                skip_reason="Job is closed",
                **job_rating_kwargs,
            )
            db.add(job_rating)
            service_log.job_skipped_ids = service_log.job_skipped_ids + [scraped_job.id]
            db.commit()
            return

        # Check that the job description is not too short
        if scraped_job.description and len(scraped_job.description) < settings.min_scraping_description_length:
            self.logger.info(f"Skipping job ID {scraped_job.id} as its description is too short")
            job_rating = models.JobRating(
                is_skipped=True,
                skip_reason=f"Job description too short (minimum length is {settings.min_scraping_description_length} characters)",
                **job_rating_kwargs,
            )
            db.add(job_rating)
            service_log.job_skipped_ids = service_log.job_skipped_ids + [scraped_job.id]
            db.commit()
            return

        # Ensure that the job has a description
        if not scraped_job.description:
            self.logger.info(f"Skipping job ID {scraped_job.id} as it has no description")
            job_rating = models.JobRating(
                is_skipped=True,
                skip_reason="Job has no description",
                **job_rating_kwargs,
            )
            db.add(job_rating)
            service_log.job_skipped_ids = service_log.job_skipped_ids + [scraped_job.id]
            db.commit()
            return

        description, description_note = ensure_length_limit(
            "description", scraped_job.description, settings.max_scraping_description_length, self.logger
        )
        if description_note:
            notes.append(description_note)
        title, title_note = ensure_length_limit(
            "title", scraped_job.title, settings.max_scraping_title_length, self.logger
        )
        if title_note:
            notes.append(title_note)
        company, company_note = ensure_length_limit(
            "company", scraped_job.company, settings.max_scraping_company_length, self.logger
        )
        if company_note:
            notes.append(company_note)

        if notes:
            job_rating_kwargs["notes"] = notes

        score = None
        try:
            self.logger.info(f"Scoring job ID {scraped_job.id}")
            job_prompt = create_job_only_prompt(
                prompt_template=job_prompt_template.prompt,
                job_title=title,
                job_company=company,
                job_description=description,
            )
            score = claude_query(combined_system_prompt, job_prompt)
            job_rating = models.JobRating(
                overall_score=score["overall_score"],
                technical_score=score["technical_fit"],
                experience_score=score["experience_alignment"],
                educational_score=score["educational_match"],
                interest_score=score["interest_match"],
                feedback=score["explanation"],
                job_prompt=combined_system_prompt + "\n\n" + job_prompt,
                is_success=True,
                **job_rating_kwargs,
            )
            db.add(job_rating)
            service_log.job_succeeded_ids = service_log.job_succeeded_ids + [scraped_job.id]
            db.commit()
        except Exception as exception:
            tb = traceback.format_exc()
            self.logger.exception(f"Error in rating workflow: {exception}")
            job_rating = models.JobRating(
                is_success=False,
                error=f"Error scoring job: {exception}\n{tb}\nRaw response is {score}",
                **job_rating_kwargs,
            )
            db.add(job_rating)
            service_log.job_failed_ids = service_log.job_failed_ids + [scraped_job.id]
            db.commit()


job_rating_service_runner = ServiceRunner(
    service_name=SERVICE_NAME,
    service_function=ScrapedJobRater().run,
)
