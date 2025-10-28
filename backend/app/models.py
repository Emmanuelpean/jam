"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

import re
from typing import Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    TIMESTAMP,
    text,
    CheckConstraint,
    Table,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.database import Base

# ------------------------------------------------------ MAPPINGS ------------------------------------------------------


job_keyword_mapping = Table(
    "job_keyword_mapping",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("job.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keyword.id", ondelete="CASCADE"), primary_key=True),
)

interview_interviewer_mapping = Table(
    "interview_interviewer_mapping",
    Base.metadata,
    Column("interview_id", Integer, ForeignKey("interview.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Integer, ForeignKey("person.id", ondelete="CASCADE"), primary_key=True),
)

job_contact_mapping = Table(
    "job_contact_mapping",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("job.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Integer, ForeignKey("person.id", ondelete="CASCADE"), primary_key=True),
)


# -------------------------------------------------------- BASES -------------------------------------------------------


class CommonBase(object):
    """A base class that contains common attributes shared by all tables.
    The table name is automatically generated from the class name by converting CamelCase to snake_case.

    Attributes:
    -----------
    - `id` (int): Primary key of the record. Automatically populated upon creation.
    - `created_at` (datetime): The timestamp of when the record was created. Automatically populated upon creation.
    - `modified_at` (datetime): The timestamp of when the record was modified. Automatically updated upon updates."""

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls) -> str:
        """Return the class name as table name e.g. JobApplication -> job_application"""

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    modified_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Owned(CommonBase):
    """A base class that contains common attributes shared by tables which entries have an owner.

    Attributes:
    -----------
    - `owner_id` (int): Foreign key linking the record to the user table."""

    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)


# --------------------------------------------------------- APP --------------------------------------------------------


class Setting(CommonBase, Base):
    """Represents the application settings

    Attributes:
    -----------
    - `name` (str, unique): The name of the setting.
    - `value` (float): The value of the setting.
    - `description` (str): A description of the setting.
    - `is_active` (bool): Indicates whether the setting is active."""

    name = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())


def get_setting(
    db,
    name: str,
    default: Any,
):
    """Retrieve a setting value from the database by its name.
    :param db: Database session.
    :param name: The name of the setting to retrieve.
    :param default: The default value to return if the setting is not found."""

    entry = db.query(Setting).filter(Setting.name == name).first()
    if entry:
        return entry.value
    else:
        return default


class User(CommonBase, Base):
    """Represents users of the application.

    Attributes:
    -----------
    - `password` (str): Encrypted password for authentication.
    - `email` (str, unique): User's email address.
    - `theme` (str): The theme of the application.
    - `is_admin` (bool): Indicates whether the user is an administrator.
    - `is_active` (bool): Indicates whether the user account is active.
    - `last_login` (datetime, optional): The timestamp of the last login.
    - `chase_threshold` (int): The threshold for chasing jobs in the dashboard.
    - `deadline_threshold` (int): The threshold for deadlines in the dashboard.
    - `update_limit` (int): Max number updates displayed in the dashboard.
    - `toast_active` (bool): Indicates whether the TOAST feature is active.
    - `default_currency` (str): The default currency for salary fields.
    - `is_verified` (bool): Indicates whether the user's email is verified.
    - `verification_token` (str, optional): Token used for email verification.
    - `verification_token_created_at` (datetime, optional): Timestamp of when the verification token was created.
    - `password_reset_token` (str, optional, unique): Token used for password reset.
    - `password_reset_token_created_at` (datetime, optional): Timestamp of when the password reset token was created.

    Constraints:
    ------------
    - Minimum password length is enforced based on environment variables."""

    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    theme = Column(String, nullable=False, server_default="mixed-berry")
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    is_admin = Column(Boolean, nullable=False, server_default=expression.false())
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    chase_threshold = Column(Integer, nullable=False, server_default="30")
    deadline_threshold = Column(Integer, nullable=False, server_default="30")
    update_limit = Column(Integer, nullable=False, server_default="10")
    toast_active = Column(Boolean, nullable=False, server_default=expression.false())
    default_currency = Column(String, nullable=False, server_default="GBP")
    is_verified = Column(Boolean, nullable=False, server_default=expression.false())
    verification_token = Column(String, nullable=True)
    verification_token_created_at = Column(TIMESTAMP(timezone=True), nullable=True)
    password_reset_token = Column(String, nullable=True, unique=True)
    password_reset_token_created_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (Index("ix_user_email_lower", func.lower(email), unique=True),)


# -------------------------------------------------------- DATA --------------------------------------------------------


class Keyword(Owned, Base):
    """Represents keywords associated with job postings.

    Attributes:
    -----------
    - `name` (str): The keyword name.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the keyword.

    Constraints:
    ------------
    - Combination of owner_id and name must be unique to prevent duplicate keywords for the same user."""

    name = Column(String, nullable=False)

    # Relationships
    jobs = relationship("Job", secondary=job_keyword_mapping, back_populates="keywords")

    # Constraints
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_owner_keyword_name"),)


class Aggregator(Owned, Base):
    """Represents an aggregator website (e.g. LinkedIn, Indeed).

    Attributes:
    -----------
    - `name` (str): The website's name.
    - `url` (str): The website's URL.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the aggregator.
    - `job_applications` (list of Job): List of jobs associated with the aggregator.

    Constraints:
    ------------
    - Combination of owner_id and name must be unique to prevent duplicate aggregators for the same user."""

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    # Relationships
    jobs = relationship("Job", foreign_keys="Job.source_id", back_populates="source")
    job_applications = relationship(
        "Job", foreign_keys="Job.application_aggregator_id", back_populates="application_aggregator"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_owner_aggregator_name"),)


class Company(Owned, Base):
    """Represents a company or organisation.

    Attributes:
    -----------
    - `name` (str, unique): Name of the company.
    - `description` (str, optional): Description or details about the company.
    - `url` (str, optional): Web link to the company's website.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the company.
    - `persons` (list of Person): List of people linked to the company.

    Constraints:
    ------------
    - Combination of owner_id and name must be unique to prevent duplicate companies for the same user."""

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="company")
    persons = relationship("Person", back_populates="company")

    # Constraints
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_owner_company_name"),)


class Location(Owned, Base):
    """Represents geographical locations.

    Attributes:
    -----------
    - `postcode` (str, optional): Postcode of the location.
    - `city` (str, optional): City of the location.
    - `country` (str, optional): Country where the location resides.
    - `name` (str): Computed property combining city, country, and postcode

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the location.
    - `interviews` (list of Interview): List of interviews associated with the location.

    Constraints:
    ------------
    - At least one of postcode, city, or country must be provided.
    - Combination of owner_id, city, postcode, and country must be unique to prevent duplicate locations for the same user.
    """

    postcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="location")
    interviews = relationship("Interview", back_populates="location")

    @hybrid_property
    def name(self) -> str:
        """Computed property that combines city, country, and postcode into a readable location name"""

        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        if self.postcode:
            parts.append(self.postcode)

        return ", ".join(parts)

    __table_args__ = (
        CheckConstraint(
            "postcode IS NOT NULL OR city IS NOT NULL OR country IS NOT NULL",
            name=f"location_data_required",
        ),
        UniqueConstraint("owner_id", "city", "postcode", "country", name="uq_owner_location_unique"),
    )


class File(Owned, Base):
    """Represents files uploaded by the users.

    Attributes:
    -----------
    - `filename` (str): Name of the file.
    - `content` (bytes): Content of the file.
    - `type` (str): MIME type of the file.
    - `size` (int): Size of the file in bytes."""

    filename = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)


class Person(Owned, Base):
    """Represents a person

    Attributes:
    -----------
    - `first_name` (str): First name of the person.
    - `last_name` (str): Last name of the person.
    - `email` (str, optional): Email address of the person.
    - `phone` (str, optional): Phone number of the person.
    - `role` (str, optional): Role or position held by the person within the company.
    - `linkedin_url` (str, optional): LinkedIn profile URL of the person.
    - `name` (str): Computed property combining first and last name.
    - `name_company` (str): Computed property combining first name, last name, and company name.

    Foreign keys:
    -------------
    - `company_id` (int): Foreign key linking the person to a company.

    Relationships:
    --------------
    - `company` (Company): Relationship to access the associated company.
    - `interviews` (list of Interview): List of interviews performed by the person within the company.
    - `jobs` (list of Job): List of jobs linked to the person within the company."""

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    company = relationship("Company", back_populates="persons")
    interviews = relationship("Interview", secondary=interview_interviewer_mapping, back_populates="interviewers")
    jobs = relationship("Job", secondary=job_contact_mapping, back_populates="contacts")

    @hybrid_property
    def name(self) -> str:
        """Computed property that combines the first and last name"""

        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def name_company(self) -> str:
        """Computed property that combines the first name, last name, and the company name"""

        if self.company:
            return f"{self.first_name} {self.last_name} - {self.company.name}"
        else:
            return self.name


class Job(Owned, Base):
    """Represents job postings within the application.

    Attributes:
    -----------
    - `title` (str): The job title.
    - `description` (str, optional): Description or details about the job.
    - `salary_min` (float, optional): Minimum salary offered for the job (in GBP).
    - `salary_max` (float, optional): Maximum salary offered for the job (in GBP).
    - `url` (str, optional): Web link to the job posting.
    - `personal_rating` (int, optional): Personalised rating given to the job.
    - `note` (str, optional): Additional note about the job posting.
    - `deadline` (datetime, optional): Deadline for the job application.
    - `followup_snooze_datetime` (datetime, optional): Date and time to snooze follow-up reminders.
    - `attendance_type` (str, optional): Type of attendance offered for the job (on-site, remote, hybrid).
    - `name` (str): Computed property combining the job title and company name.
    - `application_date` (datetime, optional): Date when the application was submitted.
    - `application_url` (str, optional): URL used to submit the application.
    - `application_status` (str, optional): Current status of the job application
    - `applied_via` (str, optional): Method used to apply for the job.
    - `application_note` (str, optional): Additional note about the job application.

    Foreign keys:
    -------------
    - `company_id` (int, optional): Identifier for the company offering the job.
    - `location_id` (int, optional): Identifier for the geographical location where the job is located.
    - `duplicate_id` (int, optional): Identifier for a duplicate job posting.
    - `source_id` (int, optional): Identifier for the aggregator website where the job was posted.
    - `application_aggregator_id` (int, optional): Identifier for the aggregator website used to apply for the job.
    - `cv_id` (int, optional): Identifier for the CV file used in the job application.
    - `cover_letter_id` (int, optional): Identifier for the cover letter file used in the job application.

    Relationships:
    --------------
    - `company` (Company): Company object associated with the job posting.
    - `location` (Location): Location object associated with the job posting.
    - `keywords` (list of Keyword): List of keywords associated with the job posting.
    - `contacts` (list of Person): List of people linked to the company that may be interested in the job posting.
    - `source` (Aggregator): Source of the job posting (e.g. LinkedIn, Indeed, etc.).
    - `interviews` (list of Interview): List of interviews associated with the job application.
    - `updates` (list of JobApplicationUpdate): List of updates associated with the job application.
    - `application_aggregator` (Aggregator): Source used to apply for the job.
    - `application_cv` (File): CV file used in the job application.
    - `application_cover_letter` (File): Cover letter file used in the job application.

    Constraints:
    ------------
    - `personal_rating` must be between 1 and 5 if provided.
    - `salary_min` must be less than or equal to `salary_max` if both are provided.
    - `attendance_type` must be one of 'on-site', 'remote', or 'hybrid' if provided.
    - `application_status` must be one of 'applied', 'interview', 'offer', 'rejected' or 'withdrawn' if provided.
    - `applied_via` must be one of 'aggregator', 'email', 'phone', or 'other' if provided."""

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String, nullable=True)
    url = Column(String, nullable=True)
    personal_rating = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    followup_snooze_datetime = Column(TIMESTAMP(timezone=True), nullable=True)
    attendance_type = Column(String, nullable=True)

    # Application specific fields
    application_date = Column(TIMESTAMP(timezone=True), nullable=True)
    application_url = Column(String, nullable=True)
    application_status = Column(String, nullable=True)
    applied_via = Column(String, nullable=True)
    application_note = Column(String, nullable=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True)
    duplicate_id = Column(Integer, ForeignKey("job.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True, index=True)
    application_aggregator_id = Column(
        Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True, index=True
    )
    cv_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)
    cover_letter_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    location = relationship("Location", back_populates="jobs")
    keywords = relationship("Keyword", secondary=job_keyword_mapping, back_populates="jobs", lazy="selectin")
    contacts = relationship("Person", secondary=job_contact_mapping, back_populates="jobs", lazy="selectin")
    source = relationship("Aggregator", foreign_keys=[source_id], back_populates="jobs")
    interviews = relationship("Interview", back_populates="job")
    updates = relationship("JobApplicationUpdate", back_populates="job")
    application_aggregator = relationship(
        "Aggregator", foreign_keys=[application_aggregator_id], back_populates="job_applications"
    )
    application_cv = relationship("File", foreign_keys=[cv_id], lazy="select")
    application_cover_letter = relationship("File", foreign_keys=[cover_letter_id], lazy="select")

    @hybrid_property
    def name(self) -> str | Column[str]:
        """Computed property that combines the job title and company name"""

        if hasattr(self, "company") and self.title and self.company and self.company.name:
            return f"{self.title} - {self.company.name}"
        elif self.title:
            return self.title
        else:
            return "Unknown Job"

    __table_args__ = (
        CheckConstraint("personal_rating >= 1 AND personal_rating <= 5", name=f"valid_rating_range"),
        CheckConstraint("salary_min <= salary_max", name=f"valid_salary_range"),
        CheckConstraint("attendance_type IN ('on-site', 'remote', 'hybrid')", name="valid_attendance_type_values"),
        CheckConstraint(
            "application_status IN ('applied', 'interview', 'offer', 'rejected', 'withdrawn')",
            name="valid_application_status_values",
        ),
        CheckConstraint("applied_via IN ('aggregator', 'email', 'phone', 'other')", name="valid_applied_via_values"),
    )


class Interview(Owned, Base):
    """Represents interviews for job applications.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the interview.
    - `type` (str): Type of the interview (HR, technical, management, ...)
    - `note` (str, optional): Additional notes or comments about the interview.
    - `attendance_type` (str, optional): The attendance type of the interview (on-site, remote).

    Foreign keys:
    -------------
    - `location_id` (int): Identifier for the location of the interview.
    - `job_id` (int): Identifier for the job application associated with the interview.

    Relationships:
    --------------
    - `job` (Job): Job object related to the interview.
    - `interviewers` (list of Person): List of people who participated in the interview.
    - `location` (Location): Location object related to the interview.

    Constraints:
    ------------
    - `attendance_type` must be one of 'on-site' or 'remote' if provided."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    type = Column(String, nullable=False)
    note = Column(String, nullable=True)
    attendance_type = Column(String, nullable=True)

    # Foreign keys
    location_id = Column(Integer, ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True)
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    location = relationship("Location", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    interviewers = relationship("Person", secondary=interview_interviewer_mapping, back_populates="interviews")

    __table_args__ = (CheckConstraint("attendance_type IN ('on-site', 'remote')", name="valid_attendance_type_values"),)


class JobApplicationUpdate(Owned, Base):
    """Represents an update to a job application.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the update.
    - `note` (str, optional): Additional notes or comments about the update.
    - `type` (str): The type of the update (received, sent).

    Foreign keys:
    -------------
    - job_id (int): Identifier for the job application associated with the update.

    Relationships:
    --------------
    - `job` (Job): Job object related to the update.

    Constraints:
    ------------
    - `type` must be one of 'received' or 'sent'."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    note = Column(String, nullable=True)
    type = Column(String, nullable=False)

    # Foreign keys
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="updates")

    __table_args__ = (CheckConstraint("type IN ('received', 'sent')", name="valid_update_type_values"),)
