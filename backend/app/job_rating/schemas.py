"""Job Rating schemas"""

import datetime as dt

from pydantic import BaseModel

from app.schemas import Out


# ----------------------------------------------------- JOB RATING -----------------------------------------------------


class JobRatingOut(BaseModel):
    """Job Rating output schema"""

    overall_score: int | None
    technical_score: int | None
    experience_score: int | None
    educational_score: int | None
    interest_score: int | None
    feedback: str | None
    script_version: int | None
    is_success: bool | None
    error: str | None
    scraped_job_id: int | None
    user_qualification_id: int | None


# ----------------------------------------------- JOB RATING SERVICE LOG -----------------------------------------------


class JobRatingServiceLogOut(Out):
    """Job Rating Service Log output schema"""

    run_datetime: dt.datetime
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None
    rated_job_found_ids: list[int] = []
    rated_job_succeeded_ids: list[int] = []
    rated_job_failed_ids: list[int] = []
    rated_job_skipped_ids: list[int] = []


class JobRatingServiceLogStartRequest(BaseModel):
    """Job Rating Service Log start request schema"""

    period_hours: int | None = 3
