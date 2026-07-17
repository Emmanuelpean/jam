"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models
from app.base_models import ProcessingStatus
from app.config import settings
from app.database import db_session
from app.job_rating.claude import MODEL as CLAUDE_MODEL, claude_query
from app.job_rating.prompts import create_job_only_prompt, create_system_prompt_with_profile
from app.service.models import ServiceErrorLevel, record_error
from app.job_rating.schemas import JobRatingServiceLogOut
from app.service.registry import register_service
from app.service.service import BaseService

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
    """Get all scraped jobs for a user that still need rating.
    A job needs rating if it has no JobRating yet, or its JobRating is still pending
    (not yet succeeded, failed-out, or skipped) and is due for another retry.
    :param db: Database session
    :param user_id: ID of the user to get jobs for
    :return: List of scraped jobs to rate"""

    # noinspection PyComparisonWithNone
    return (
        db.query(models.ScrapedJob)
        .outerjoin(models.JobRating, models.JobRating.scraped_job_id == models.ScrapedJob.id)
        .filter(models.ScrapedJob.owner_id == user_id)
        .filter(models.ScrapedJob.status == ProcessingStatus.COMPLETED)
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.exclusion_filter == None)
        .filter(or_(models.JobRating.id == None, models.JobRating.is_pending))
        .all()
    )


class ScrapedJobRatingService(BaseService[models.JobRatingServiceLog]):
    """Rates scraped jobs against user qualifications using AI."""

    service_name = "job_rating_service"

    def __init__(self) -> None:
        """Initialise the job rater."""

        BaseService.__init__(self, models.JobRatingServiceLog)

    def run(self) -> models.JobRatingServiceLog:
        """Score all scraped jobs using AI.
        :return: Job rating service log entry"""

        with db_session() as db:
            service_log = self.start_run(db)

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

            except Exception as exception:
                message = "Critical error in rating workflow"
                self.logger.exception(message)
                record_error(
                    db,
                    exception,
                    message,
                    level=ServiceErrorLevel.CRITICAL,
                    job_rating_service_log_id=service_log.id,
                )
            finally:
                self.logger.info("Finished workflow")

            service_log.set_run_duration()
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
            .order_by(models.UserQualification.modified_at.desc(), models.UserQualification.id.desc())
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

        # Build the combined system prompt
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

        job_rating = scraped_job.job_rating
        if job_rating is None:
            job_rating = models.JobRating(
                scraped_job_id=scraped_job.id,
                owner_id=user_id,
                llm_model=CLAUDE_MODEL,
                job_prompt_template_id=job_prompt_template.id,
                system_prompt_id=system_prompt.id,
                user_qualification_id=user_qualification.id,
                service_log_id=service_log.id,
            )
            db.add(job_rating)
            db.flush()

        skip_reason = None
        # Check that the job is not closed
        if scraped_job.is_closed or (scraped_job.deadline and scraped_job.deadline < dt.datetime.now(dt.timezone.utc)):
            self.logger.info(f"Skipping job ID {scraped_job.id} as it is closed")
            skip_reason = "Job is closed"

        # Ensure that the job has a description
        elif not scraped_job.description:
            self.logger.info(f"Skipping job ID {scraped_job.id} as it has no description")
            skip_reason = "Job has no description"

        # Check that the job description is not too short
        elif len(scraped_job.description) < settings.min_scraping_description_length:
            self.logger.info(f"Skipping job ID {scraped_job.id} as its description is too short")
            skip_reason = (
                f"Job description too short (minimum length is {settings.min_scraping_description_length} characters)"
            )

        if skip_reason:
            job_rating.status = ProcessingStatus.SKIPPED
            job_rating.skip_reason = skip_reason
            service_log.job_skipped_ids = service_log.job_skipped_ids + [scraped_job.id]
            db.commit()
            return

        description, description_note = ensure_length_limit(
            "description",
            scraped_job.description,
            settings.max_scraping_description_length,
            self.logger,
        )
        if description_note:
            notes.append(description_note)
        title, title_note = ensure_length_limit(
            "title",
            scraped_job.title,
            settings.max_scraping_title_length,
            self.logger,
        )
        if title_note:
            notes.append(title_note)
        company, company_note = ensure_length_limit(
            "company",
            scraped_job.company,
            settings.max_scraping_company_length,
            self.logger,
        )
        if company_note:
            notes.append(company_note)

        if notes:
            job_rating.notes = notes

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
            job_rating.overall_score = score["overall_score"]
            job_rating.technical_score = score["technical_fit"]
            job_rating.experience_score = score["experience_alignment"]
            job_rating.educational_score = score["educational_match"]
            job_rating.interest_score = score["interest_match"]
            job_rating.feedback = score["explanation"]
            job_rating.job_prompt = combined_system_prompt + "\n\n" + job_prompt
            job_rating.status = ProcessingStatus.COMPLETED
            job_rating.rating_next_retry_at = None
            service_log.job_succeeded_ids = service_log.job_succeeded_ids + [scraped_job.id]
            db.commit()
        except Exception as exception:
            message = "Error scoring job."
            context = {"job_id": scraped_job.id, "error": str(exception), "raw_response": repr(score)}
            self.logger.exception(f"{message} {context}")
            record_error(
                db,
                exception,
                message=message,
                context=context,
                job_rating_id=job_rating.id,
                job_rating_service_log_id=service_log.id,
            )
            job_rating.rating_retry_count += 1
            service_log.job_failed_ids = service_log.job_failed_ids + [scraped_job.id]
            if job_rating.rating_retry_count < settings.rating_max_retry:
                job_rating.rating_next_retry_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                    hours=settings.rating_retry_delay_hours
                )
                self.logger.info(
                    f"Scheduled rating retry {job_rating.rating_retry_count}/{settings.rating_max_retry} for "
                    f"job ID {scraped_job.id} in {settings.rating_retry_delay_hours}h"
                )
            else:
                self.logger.info(
                    f"Job ID {scraped_job.id} rating permanently failed after {settings.rating_max_retry} attempts"
                )
                job_rating.status = ProcessingStatus.FAILED
            db.commit()


register_service(
    ScrapedJobRatingService.service_name,
    ScrapedJobRatingService().run,
    display_name="Job Rating",
    run_period_hours=3,
    log_model=models.JobRatingServiceLog,
    log_schema=JobRatingServiceLogOut,
)
