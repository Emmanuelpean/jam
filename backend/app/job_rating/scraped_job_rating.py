"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt
import traceback

from sqlalchemy.orm import Session

from app import models as models
from app import utils
from app.config import settings
from app.database import get_db
from app.job_rating.chatgpt import openai_query
from app.job_rating.prompts import create_ai_prompt
from app.service_runner.service_runner import ServiceRunner

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

    if len(text) > max_length:
        if logger:
            logger.info(f"Job {text_describer} is too long ({len(text)}.")
        text = text[:max_length] + "..."
        note = f"{text_describer.capitalize()} was truncated as it was too long ({len(text)} characters. Limit is {max_length} characters)"
        return text, note
    else:
        return text, None


def score_scraped_jobs(db: Session | None = None) -> models.JobRatingServiceLog:
    """Score all scraped jobs using Gemini LLM.
    :param db: Database session
    :return: Job rating service log entry"""

    db = next(get_db()) if db is None else db
    logger = utils.AppLogger.create_service_logger(SERVICE_NAME, "INFO")

    # Create service log entry
    start_time = dt.datetime.now()
    service_log = models.JobRatingServiceLog(run_datetime=start_time)
    db.add(service_log)
    db.commit()
    db.refresh(service_log)

    try:
        # Get all active users
        users = (
            db.query(models.User)
            .filter(models.User.premium.has(is_active=True, job_rating_active=True))
            .filter(models.User.is_active)
            .filter(models.User.is_verified)
            .all()
        )
        logger.info(f"Found {len(users)} active users to process")
        service_log.user_found_ids = [user.id for user in users]

        # Get the latest system prompt and job prompt template
        system_prompt = db.query(models.AiSystemPrompt).order_by(models.AiSystemPrompt.id.desc()).first()
        job_prompt_template = (
            db.query(models.AiJobPromptTemplate).order_by(models.AiJobPromptTemplate.id.desc()).first()
        )

        for user in users:
            # Get the most recent qualification for the user
            user_qualification = (
                db.query(models.UserQualification)
                .filter(models.UserQualification.owner_id == user.id)
                .order_by(models.UserQualification.modified_at.desc())
                .first()
            )
            if user_qualification:
                logger.info(f"Processing user {user.id}")

                # Find scraped jobs for this user that need rating
                # noinspection PyComparisonWithNone
                scraped_jobs = (
                    db.query(models.ScrapedJob)
                    .filter(models.ScrapedJob.owner_id == user.id)  # for this user
                    .filter(models.ScrapedJob.is_processed.is_(True))  # processed
                    .filter(models.ScrapedJob.is_scraped.is_(True))  # scraped
                    .filter(models.ScrapedJob.is_failed.is_(False))  # not failed
                    .filter(models.ScrapedJob.job_rating == None)  # not yet rated
                    .filter(models.ScrapedJob.is_active.is_(True))  # active
                    .filter(models.ScrapedJob.is_imported.is_(False))  # not imported
                    .filter(models.ScrapedJob.exclusion_filter == None)  # not filtered out
                    .all()
                )
                service_log.job_found_ids = service_log.job_found_ids + [job.id for job in scraped_jobs]
                logger.info(f"Found {len(scraped_jobs)} scraped jobs to rate")

                # Rate each job
                for scraped_job in scraped_jobs:
                    logger.info(f"Processing job ID {scraped_job.id}")
                    scraping_notes = []

                    job_rating_kwargs = dict(
                        scraped_job_id=scraped_job.id,
                        owner_id=user.id,
                        user_qualification_id=user_qualification.id,
                        system_prompt_id=system_prompt.id,
                        job_prompt_template_id=job_prompt_template.id,
                    )

                    if len(scraped_job.description) < settings.min_scraping_description_length:
                        logger.info(f"Skipping job ID {scraped_job.id} as its description is too short")
                        job_rating = models.JobRating(
                            is_skipped=True,
                            skip_reason="Job description too short",
                            **job_rating_kwargs,
                        )
                        db.add(job_rating)
                        service_log.job_skipped_ids = service_log.job_skipped_ids + [scraped_job.id]
                        continue

                    # Ensure that the job description and title are not too long
                    description, description_note = ensure_length_limit(
                        "description", scraped_job.description, settings.max_scraping_description_length, logger
                    )
                    if description_note:
                        scraping_notes.append(description_note)
                    title, title_note = ensure_length_limit(
                        "title", scraped_job.title, settings.max_scraping_title_length, logger
                    )
                    if title_note:
                        scraping_notes.append(title_note)
                    company, company_note = ensure_length_limit(
                        "company", scraped_job.company, settings.max_scraping_company_length, logger
                    )
                    if company_note:
                        scraping_notes.append(company_note)

                    score = None
                    try:
                        logger.info(f"Scoring job ID {scraped_job.id}")
                        job_prompt = create_ai_prompt(
                            job_prompt_template.prompt,
                            user_qualification.experience,
                            user_qualification.education,
                            user_qualification.skills,
                            user_qualification.qualities,
                            user_qualification.interests,
                            title,
                            company,
                            description,
                        )
                        score = openai_query(system_prompt.prompt, job_prompt)
                        job_rating = models.JobRating(
                            overall_score=score["overall_score"],
                            technical_score=score["technical_fit"],
                            experience_score=score["experience_alignment"],
                            educational_score=score["educational_match"],
                            interest_score=score["interest_match"],
                            feedback=score["explanation"],
                            job_prompt=job_prompt,
                            is_success=True,
                            **job_rating_kwargs,
                        )
                        db.add(job_rating)
                        db.commit()
                        service_log.rated_job_succeeded_ids = service_log.job_succeeded_ids + [scraped_job.id]
                    except Exception as exception:
                        tb = traceback.format_exc()
                        logger.exception(f"Error in rating workflow: {exception}")
                        job_rating = models.JobRating(
                            is_success=False,
                            error=f"Error scoring job: {exception}\n{tb}\nRaw response is {score}",
                            **job_rating_kwargs,
                        )
                        db.add(job_rating)
                        db.commit()
                        service_log.rated_job_failed_ids = service_log.rated_job_failed_ids + [scraped_job.id]

                service_log.user_processed_ids = service_log.user_processed_ids + [user.id]

            else:
                logger.info(f"Skipping user {user.id} as no user qualification found")

        # Log final statistics
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = True

    except Exception as exception:
        logger.exception(f"Critical error in rating workflow: {exception}")
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = False
        service_log.error_message = str(exception)
    finally:
        logger.info("Finished workflow")

    db.commit()
    db.refresh(service_log)
    return service_log


job_rating_service_runner = ServiceRunner(
    service_name=SERVICE_NAME,
    service_function=score_scraped_jobs,
)

if __name__ == "__main__":
    score_scraped_jobs()
