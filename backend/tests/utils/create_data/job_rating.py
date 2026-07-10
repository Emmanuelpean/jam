"""Functions for creating job rating service test data."""

from app import models
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import job_rating


def create_job_rating_service_logs(db) -> list[models.JobRatingServiceLog]:
    """Create sample job scraping service logs"""

    data = job_rating.JOB_RATING_SERVICE_LOG_DATA
    print(f"Creating {len(data)} Job Rating Service Logs...")
    return create_db_entries(db, models.JobRatingServiceLog, data)


def create_job_rating_service_errors(db, service_logs) -> list[models.ServiceError]:
    """Create sample run-level job rating errors as unified ServiceError rows linked to their service log"""

    data = override_properties(
        job_rating.JOB_RATING_SERVICE_ERROR_DATA,
        ("job_rating_service_log_id", service_logs),
    )
    print(f"Creating {len(data)} Job Rating Service Errors...")
    return create_db_entries(db, models.ServiceError, data)


def create_job_rating_errors(db, job_ratings, service_logs) -> list[models.ServiceError]:
    """Create sample per-rating job rating errors as unified ServiceError rows linked to their JobRating and to the
    rating run that processed it, mirroring how the rater records per-job failures in production. The owning run is
    the service log whose job_failed_ids contains the rating's scraped job."""

    data = override_properties(job_rating.JOB_RATING_ERROR_DATA, ("job_rating_id", job_ratings))
    rating_by_id = {rating.id: rating for rating in job_ratings}
    for entry in data:
        scraped_job_id = rating_by_id[entry["job_rating_id"]].scraped_job_id
        log = next((sl for sl in service_logs if scraped_job_id in sl.job_failed_ids), None)
        entry["job_rating_service_log_id"] = log.id if log else None
    print(f"Creating {len(data)} Job Rating Errors...")
    return create_db_entries(db, models.ServiceError, data)


def create_job_ratings(db, users, use_qualifications, scraped_jobs, service_logs, ai_prompts) -> list[models.JobRating]:
    """Create sample job ratings"""

    data = override_properties(
        job_rating.JOB_RATING_DATA,
        ("owner_id", users),
        ("job_id", scraped_jobs),
        ("user_qualification_id", use_qualifications),
        ("service_log_id", service_logs),
    )
    print(f"Creating {len(data)} Job Ratings...")
    job_ratings = create_db_entries(db, models.JobRating, data)

    # Assign AI prompts if provided
    if job_ratings:
        system_prompt, job_template = ai_prompts
        for rating in job_ratings:
            rating.system_prompt_id = system_prompt.id
            rating.job_prompt_template_id = job_template.id
        db.commit()

    return job_ratings
