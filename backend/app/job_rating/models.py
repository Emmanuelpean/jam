"""Database models for job ratings and their service logs."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship

from app.database import Base
from app.models import Owned


class JobRating(Owned, Base):
    """Represents user ratings for jobs.

    Attributes:
    -----------
    - `overall_score` (int): Overall score for the job.
    - `technical_score` (int, optional): Technical score for the job.
    - `experience_score` (int, optional): Experience score for the job.
    - `educational_score` (int, optional): Educational score for the job.
    - `interest_score` (int, optional): Interest score for the job.
    - `feedback` (str, optional): Additional feedback or comments about the job rating.
    - `script_version` (int, optional): Version of the rating script used.
    - `is_success` (bool, optional): Indicates whether the rating process was successful.
    - `error` (str, optional): Error message if the rating process failed.

    Foreign keys:
    -------------
    - `scraped_job_id` (int): Identifier for the job being rated.
    - `user_qualification_id` (int): Identifier for the user qualification entry used to rate the job

    Relationships:
    --------------
    - `scraped_job` (ScrapedJob): ScrapedJob object related to the rating.
    - `use_qualification` (UserQualification): UserQualification object related to the rating."""

    overall_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    experience_score = Column(Integer, nullable=True)
    educational_score = Column(Integer, nullable=True)
    interest_score = Column(Integer, nullable=True)
    feedback = Column(String, nullable=True)
    script_version = Column(Integer, nullable=True)
    is_success = Column(Boolean, nullable=True)
    error = Column(String, nullable=True)

    # Foreign keys
    scraped_job_id = Column(Integer, ForeignKey("scraped_job.id", ondelete="CASCADE"), nullable=False)
    user_qualification_id = Column(Integer, ForeignKey("user_qualification.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    scraped_job = relationship("ScrapedJob")
    user_qualification = relationship("UserQualification")


class JobRatingServiceLog(Owned, Base):
    """Represents service logs for job ratings.

    Attributes:
    -----------
    - `request_payload` (str): The request payload sent to the rating service.
    - `response_payload` (str): The response payload received from the rating service.
    - `status_code` (int): The HTTP status code of the response.
    - `error_message` (str, optional): Any error message returned by the service.

    Foreign keys:
    -------------
    - `job_rating_id` (int): Identifier for the job rating associated with the log.

    Relationships:
    --------------
    - `job_rating` (JobRating): JobRating object related to the service log."""

    run_duration = Column(Float, nullable=True)
    run_datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    is_success = Column(Boolean, nullable=True)
    error_message = Column(String, nullable=True)

    rated_job_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_succeeded_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_failed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_skipped_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("rated_job_found_ids", [])
        kwargs.setdefault("rated_job_succeeded_ids", [])
        kwargs.setdefault("rated_job_failed_ids", [])
        kwargs.setdefault("rated_job_skipped_ids", [])
        super().__init__(**kwargs)
