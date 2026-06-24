"""Job Rating schemas"""

import datetime as dt

from pydantic import BaseModel

from app.base_schemas import Out
from app.service_runner.schemas import ErrorOut, ServiceLogOut

# ----------------------------------------------------- JOB RATING -----------------------------------------------------


class JobRatingOut(BaseModel):
    """Job Rating output schema"""

    overall_score: int | None
    technical_score: int | None
    experience_score: int | None
    educational_score: int | None
    interest_score: int | None
    feedback: str | None
    is_success: bool | None
    is_skipped: bool | None
    skip_reason: str | None
    scraped_job_id: int | None
    user_qualification_id: int | None
    system_prompt_id: int | None
    job_prompt_template_id: int | None
    job_prompt: str | None
    notes: list[str] = []
    rating_retry_count: int = 0
    rating_next_retry_at: dt.datetime | None = None
    rating_errors: list[ErrorOut] = []


# ----------------------------------------------- JOB RATING SERVICE LOG -----------------------------------------------


class JobRatingServiceLogOut(ServiceLogOut):
    """Job Rating Service Log output schema"""

    job_found_ids: list[int] = []
    job_succeeded_ids: list[int] = []
    job_failed_ids: list[int] = []
    job_skipped_ids: list[int] = []
    user_found_ids: list[int] = []
    user_processed_ids: list[int] = []


class JobRatingServiceLogStartRequest(BaseModel):
    """Job Rating Service Log start request schema"""

    period_hours: int = 3
