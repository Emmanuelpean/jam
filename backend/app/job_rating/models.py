"""Database models for job ratings and their service logs."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship

from app.database import Base
from app.base_models import Owned, CommonBase
from app.service_runner.models import ServiceLog


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
    scraped_job = relationship("ScrapedJob", back_populates="job_rating")
    user_qualification = relationship("UserQualification", back_populates="job_ratings")


class JobRatingServiceLog(ServiceLog, CommonBase, Base):
    """Represents service logs for job ratings.

    Attributes:
    -----------
    - `user_found_ids` (List[int]): List of user IDs that were found during the processing.
    - `user_processed_ids` (List[int]): List of user IDs that were processed.
    - `rated_job_found_ids` (List[int]): List of job IDs that were found during the rating process.
    - `rated_job_succeeded_ids` (List[int]): List of job IDs that were successfully rated.
    - `rated_job_failed_ids` (List[int]): List of job IDs that failed to be rated."""

    user_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    user_processed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_succeeded_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    rated_job_failed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("user_found_ids", [])
        kwargs.setdefault("user_processed_ids", [])
        kwargs.setdefault("rated_job_found_ids", [])
        kwargs.setdefault("rated_job_succeeded_ids", [])
        kwargs.setdefault("rated_job_failed_ids", [])
        super().__init__(**kwargs)
