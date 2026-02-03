"""Functions for creating job rating service test data."""

from app import models
from tests.utils.test_data import job_rating_service
from tests.utils.create_data.utils import add_to_db, override_entries_properties


def create_job_rating_service_logs(db) -> list[models.JobRatingServiceLog]:
    """Create sample scraped job service logs"""

    print("Creating Job Rating service logs...")
    # noinspection PyArgumentList
    logs = [models.JobRatingServiceLog(**log) for log in job_rating_service.JOB_RATING_SERVICE_LOG_DATA]

    return add_to_db(db, logs)


def create_job_ratings(db, users, use_qualifications, scraped_jobs, service_logs, ai_prompts) -> list[models.JobRating]:
    """Create sample job ratings"""

    print("Creating job ratings...")
    # noinspection PyArgumentList
    job_ratings = [
        models.JobRating(**kwargs)
        for kwargs in override_entries_properties(
            job_rating_service.JOB_RATING_DATA,
            ("owner_id", users),
            ("job_id", scraped_jobs),
            ("user_qualification_id", use_qualifications),
            ("service_log_id", service_logs),
        )
    ]

    # Assign AI prompts if provided
    if job_ratings:
        system_prompt, job_template = ai_prompts
        for rating in job_ratings:
            rating.system_prompt_id = system_prompt.id
            rating.job_prompt_template_id = job_template.id

    return add_to_db(db, job_ratings)
