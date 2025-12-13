"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt
import traceback

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.job_rating import models
from app import models as app_models
from app import utils
from app.database import get_db
from app.eis import models as eis_models
from app.job_rating.ai_rating import ai_score_job, __version__
from app.service_runner import ServiceRunner


SERVICE_NAME = "job_rating_service"


def score_scraped_jobs(min_description_length: int = 100, db: Session | None = None) -> models.JobRatingServiceLog:
    """Score all scraped jobs using Gemini LLM.
    :param min_description_length: Minimum job description length to consider
    :param db: Database session"""

    db = next(get_db()) if db is None else db
    logger = utils.AppLogger.create_service_logger(SERVICE_NAME, "INFO")
    start_time = dt.datetime.now()
    service_log = models.JobRatingServiceLog(run_datetime=start_time)
    db.add(service_log)

    try:
        # noinspection PyComparisonWithNone
        scraped_jobs = (
            db.query(eis_models.ScrapedJob)
            .filter(eis_models.ScrapedJob.is_scraped)  # scraped
            .filter(eis_models.ScrapedJob.is_failed.is_(False))  # not failed
            .filter(eis_models.ScrapedJob.job_rating == None)  # not yet rated
            .filter(eis_models.ScrapedJob.is_active)  # active
            .filter(eis_models.ScrapedJob.is_imported.is_(False))  # not imported
            .filter(func.length(eis_models.ScrapedJob.description) > min_description_length)  # description length
            .all()
        )
        service_log.rated_job_found_ids = [job.id for job in scraped_jobs]
        logger.info(f"Found {len(scraped_jobs)} scraped jobs to rate")

        for scraped_job in scraped_jobs:
            owner_id = scraped_job.owner_id
            owner_qualifications = (
                db.query(app_models.UserQualification)
                .filter(app_models.UserQualification.owner_id == owner_id)
                .order_by(app_models.UserQualification.modified_at.desc())
                .first()
            )
            if owner_qualifications and (
                owner_qualifications.experience
                or owner_qualifications.education
                or owner_qualifications.skills
                or owner_qualifications.qualities
            ):
                kwargs = dict(
                    scraped_job_id=scraped_job.id,
                    owner_id=owner_id,
                    script_version=__version__,
                    user_qualification_id=owner_qualifications.id,
                )
                score = None
                try:
                    logger.info(f"Scoring job ID {scraped_job.id} for owner ID {owner_id}")
                    score = ai_score_job(
                        owner_qualifications.experience,
                        owner_qualifications.education,
                        owner_qualifications.skills,
                        owner_qualifications.qualities,
                        owner_qualifications.interests,
                        scraped_job.title,
                        scraped_job.company,
                        scraped_job.description,
                    )
                    # noinspection PyArgumentList
                    job_rating = models.JobRating(
                        overall_score=score["overall_score"],
                        technical_score=score["technical_fit"],
                        experience_score=score["experience_alignment"],
                        educational_score=score["educational_match"],
                        interest_score=score["interest_match"],
                        feedback=score["explanation"],
                        is_success=True,
                        **kwargs,
                    )
                    db.add(job_rating)
                    db.commit()
                    # noinspection PyAugmentAssignment
                    service_log.rated_job_succeeded_ids = service_log.rated_job_succeeded_ids + [scraped_job.id]
                except Exception as exception:
                    tb = traceback.format_exc()
                    logger.exception(f"Error in rating workflow: {exception}")
                    # noinspection PyArgumentList
                    job_rating = models.JobRating(
                        is_success=False,
                        error=f"Error scoring job: {exception}\n{tb}\nRaw response is {score}",
                        **kwargs,
                    )
                    db.add(job_rating)
                    db.commit()
                    # noinspection PyAugmentAssignment
                    service_log.rated_job_failed_ids = service_log.rated_job_failed_ids + [scraped_job.id]
            else:
                logger.info(f"Skipping job ID {scraped_job.id} for owner ID {owner_id} due to missing qualifications")
                # noinspection PyAugmentAssignment
                service_log.rated_job_skipped_ids = service_log.rated_job_skipped_ids + [scraped_job.id]

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
    return service_log


class JobRatingServiceRunner(ServiceRunner):
    """Service runner for the LLM job rating service."""

    service_function = score_scraped_jobs
    service_name = SERVICE_NAME
    period_hours = 3.0


job_rating_service_runner = JobRatingServiceRunner()


if __name__ == "__main__":
    # service_runner = LlmJobRatingServiceRunner()
    # service_runner.start_runner(1)

    score_scraped_jobs(10)
