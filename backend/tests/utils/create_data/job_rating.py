"""Functions for creating job rating service test data."""

from app import models
from tests.utils.test_data import job_rating
from tests.utils.create_data.utils import create_db_entries, override_properties


def create_job_rating_service_logs(db) -> list[models.JobRatingServiceLog]:
    """Create sample job scraping service logs"""

    data = job_rating.JOB_RATING_SERVICE_LOG_DATA
    print(f"Creating {len(data)} Job Rating Service Logs...")
    return create_db_entries(db, models.JobRatingServiceLog, data)


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

    # Assign AI prompts if provided  # TODO
    if job_ratings:
        system_prompt, job_template = ai_prompts
        for rating in job_ratings:
            rating.system_prompt_id = system_prompt.id
            rating.job_prompt_template_id = job_template.id
        db.commit()

    return job_ratings
