"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt
import traceback

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import model_registry as models
from app import utils
from app.database import get_db
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
    db.commit()
    db.refresh(service_log)

    try:
        users = db.query(models.User).join(models.UserQualification).filter(models.User.is_active).all()
        logger.info(f"Found {len(users)} active users to process")
        service_log.user_found_ids = [user.id for user in users]
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
                    .filter(models.ScrapedJob.is_scraped)  # scraped
                    .filter(models.ScrapedJob.is_failed.is_(False))  # not failed
                    .filter(models.ScrapedJob.job_rating == None)  # not yet rated
                    .filter(models.ScrapedJob.is_active)  # active
                    .filter(models.ScrapedJob.is_imported.is_(False))  # not imported
                    .filter(func.length(models.ScrapedJob.description) > min_description_length)  # description length
                    .filter(models.ScrapedJob.exclusion_filter == None)  # not filtered out
                    .all()
                )
                # noinspection PyAugmentAssignment
                service_log.rated_job_found_ids = service_log.rated_job_found_ids + [job.id for job in scraped_jobs]
                logger.info(f"Found {len(scraped_jobs)} scraped jobs to rate")

                for scraped_job in scraped_jobs:

                    kwargs = dict(
                        scraped_job_id=scraped_job.id,
                        owner_id=user.id,
                        script_version=__version__,
                        user_qualification_id=user_qualification.id,
                    )
                    score = None
                    try:
                        logger.info(f"Scoring job ID {scraped_job.id}")
                        score = ai_score_job(
                            user_qualification.experience,
                            user_qualification.education,
                            user_qualification.skills,
                            user_qualification.qualities,
                            user_qualification.interests,
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

                # noinspection PyAugmentAssignment
                service_log.user_processed_ids = service_log.user_processed_ids + [user.id]

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


class JobRatingServiceRunner(ServiceRunner):
    """Service runner for the LLM job rating service."""

    def __init__(self) -> None:
        """Object constructor"""

        ServiceRunner.__init__(self, SERVICE_NAME, dict(), score_scraped_jobs, 3.0)


job_rating_service_runner = JobRatingServiceRunner()


if __name__ == "__main__":
    # service_runner = LlmJobRatingServiceRunner()
    # service_runner.start_runner(1)

    score_scraped_jobs(10)
