"""Database models for job ratings and their service logs."""

import datetime as dt

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    TIMESTAMP,
    and_,
    or_,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.base_models import Owned, CommonBase, ProcessingStatus
from app.database import Base
from app.service.models import ServiceLog


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
    - `status` (ProcessingStatus): Rating outcome — PENDING (not yet finalised, may be retrying),
      COMPLETED (rated successfully), FAILED (retries exhausted), or SKIPPED.
    - `skip_reason` (str, optional): Reason for skipping the rating process.
    - `job_prompt` (str, optional): Job prompt used for the rating.
    - `llm_model` (str): LLM model used for the rating.
    - `notes` (List[str], optional): Additional notes or comments about the rating.
    - `rating_retry_count` (int): Number of times the rating has been retried.
    - `rating_next_retry_at` (datetime, optional): When the next rating retry is scheduled.

    Foreign keys:
    -------------
    - `scraped_job_id` (int): Identifier for the job being rated.
    - `user_qualification_id` (int): Identifier for the user qualification entry used to rate the job
    - `system_prompt_id` (int, optional): Identifier for the AI system prompt used to rate the job.
    - `job_prompt_template_id` (int, optional): Identifier for the AI job prompt template used to rate the job.
    - `service_log_id` (int, optional): Identifier for the rating run that created this rating.

    Relationships:
    --------------
    - `scraped_job` (ScrapedJob): ScrapedJob object related to the rating.
    - `use_qualification` (UserQualification): UserQualification object related to the rating.
    - `system_prompt` (AiSystemPrompt, optional): AiSystemPrompt object related to the rating.
    - `job_prompt_template` (AiJobPromptTemplate, optional): AiJobPromptTemplate object related to the rating.
    - `service_log` (JobRatingServiceLog, optional): the rating run that created this rating.
    - `rating_errors` (list of Error): Errors raised while rating this job."""

    overall_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    experience_score = Column(Integer, nullable=True)
    educational_score = Column(Integer, nullable=True)
    interest_score = Column(Integer, nullable=True)
    feedback = Column(String, nullable=True)
    status = Column(String, nullable=False, default=ProcessingStatus.PENDING)
    skip_reason = Column(String, nullable=True)
    job_prompt = Column(String, nullable=True)
    llm_model = Column(String, nullable=False)
    notes = Column(PG_ARRAY(String), server_default="{}", nullable=False)
    rating_retry_count = Column(Integer, nullable=False, server_default="0")
    rating_next_retry_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Foreign keys
    scraped_job_id = Column(Integer, ForeignKey("scraped_job.id", ondelete="CASCADE"), nullable=False)
    user_qualification_id = Column(Integer, ForeignKey("user_qualification.id", ondelete="CASCADE"), nullable=False)
    system_prompt_id = Column(Integer, ForeignKey("ai_system_prompt.id", ondelete="SET NULL"), nullable=True)
    job_prompt_template_id = Column(
        Integer, ForeignKey("ai_job_prompt_template.id", ondelete="SET NULL"), nullable=True
    )
    service_log_id = Column(Integer, ForeignKey("job_rating_service_log.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    scraped_job = relationship("ScrapedJob", back_populates="job_rating")
    user_qualification = relationship("UserQualification", back_populates="job_ratings")
    system_prompt = relationship("AiSystemPrompt", back_populates="job_ratings")
    job_prompt_template = relationship("AiJobPromptTemplate", back_populates="job_ratings")
    service_log = relationship("JobRatingServiceLog", back_populates="job_ratings")
    rating_errors = relationship("ServiceError", foreign_keys="ServiceError.job_rating_id", back_populates="job_rating")

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("notes", [])
        super().__init__(**kwargs)

    @hybrid_property
    def is_pending(self) -> bool:
        """Whether the rating is still runnable: not yet finalised (status is PENDING) and due for a
        (re)try now."""

        now = dt.datetime.now(dt.timezone.utc)
        return self.status == ProcessingStatus.PENDING and (
            self.rating_next_retry_at is None or self.rating_next_retry_at <= now
        )

    @is_pending.expression
    def is_pending(cls):
        """SQL form of :attr:`is_pending` for use in queries."""

        return and_(
            cls.status == ProcessingStatus.PENDING,
            or_(
                cls.rating_next_retry_at.is_(None),
                cls.rating_next_retry_at <= func.now(),
            ),
        )


class JobRatingServiceLog(ServiceLog, Base):
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

    # Relationships
    service_errors = relationship("ServiceError", back_populates="job_rating_service_log", cascade="all, delete-orphan")
    job_ratings = relationship("JobRating", back_populates="service_log")

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""

        kwargs.setdefault("user_found_ids", [])
        kwargs.setdefault("user_processed_ids", [])
        kwargs.setdefault("job_found_ids", [])
        kwargs.setdefault("job_succeeded_ids", [])
        kwargs.setdefault("job_skipped_ids", [])
        kwargs.setdefault("job_failed_ids", [])
        super().__init__(**kwargs)
