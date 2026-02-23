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
from sqlalchemy.sql import expression

from app.base_models import Owned, CommonBase
from app.database import Base
from app.service_runner.models import ServiceLog


class AiSystemPrompt(CommonBase, Base):
    """Represents AI system prompts for job ratings.

    Attributes:
    -----------
    - `prompt` (str): The AI system prompt.

    Relationships
    -------------
    - `job_ratings`: JobRating that used the system prompt to rate the job"""

    prompt = Column(String, nullable=False)

    # Relationships
    job_ratings = relationship("JobRating", back_populates="system_prompt")


class AiJobPromptTemplate(CommonBase, Base):
    """Represents AI job prompt templates for job rating

    Attributes:
    -----------
    - `prompt` (str): The AI job prompt template.

    Relationships
    -------------
    - `job_ratings`: JobRating that used the system prompt to rate the job"""

    prompt = Column(String, nullable=False)

    # Relationships
    job_ratings = relationship("JobRating", back_populates="job_prompt_template")


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
    is_skipped = Column(Boolean, nullable=False, server_default=expression.false())
    skip_reason = Column(String, nullable=True)
    is_success = Column(Boolean, nullable=True)
    error = Column(String, nullable=True)
    job_prompt = Column(String, nullable=True)
    notes = Column(PG_ARRAY(String), server_default="{}", nullable=False)

    # Foreign keys
    scraped_job_id = Column(Integer, ForeignKey("scraped_job.id", ondelete="CASCADE"), nullable=False)
    user_qualification_id = Column(Integer, ForeignKey("user_qualification.id", ondelete="CASCADE"), nullable=False)
    system_prompt_id = Column(Integer, ForeignKey("ai_system_prompt.id", ondelete="SET NULL"), nullable=True)
    job_prompt_template_id = Column(
        Integer, ForeignKey("ai_job_prompt_template.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    scraped_job = relationship("ScrapedJob", back_populates="job_rating")
    user_qualification = relationship("UserQualification", back_populates="job_ratings")
    system_prompt = relationship("AiSystemPrompt", back_populates="job_ratings")
    job_prompt_template = relationship("AiJobPromptTemplate", back_populates="job_ratings")

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("notes", [])
        super().__init__(**kwargs)


class JobRatingServiceLog(ServiceLog, CommonBase, Base):
    """Represents service logs for job ratings.

    Attributes:
    -----------
    - `user_found_ids` (List[int]): List of user IDs that were found during the processing.
    - `user_processed_ids` (List[int]): List of user IDs that were processed.
    - `job_found_ids` (List[int]): List of job IDs that were found during the rating process.
    - `job_succeeded_ids` (List[int]): List of job IDs that were successfully rated.
    - `job_skipped_ids` (List[int]): List of job IDs that were skipped during the rating process.
    - `job_failed_ids` (List[int]): List of job IDs that failed to be rated."""

    user_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    user_processed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_succeeded_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_skipped_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_failed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("user_found_ids", [])
        kwargs.setdefault("user_processed_ids", [])
        kwargs.setdefault("job_found_ids", [])
        kwargs.setdefault("job_succeeded_ids", [])
        kwargs.setdefault("job_skipped_ids", [])
        kwargs.setdefault("job_failed_ids", [])
        super().__init__(**kwargs)
