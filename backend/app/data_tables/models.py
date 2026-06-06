"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

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
    UniqueConstraint,
    JSON,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.base_models import CommonBase, Owned
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

speculative_application_contact_mapping = Table(
    "speculative_application_contact_mapping",
    Base.metadata,
    Column(
        "speculative_application_id",
        Integer,
        ForeignKey("speculative_application.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("person_id", Integer, ForeignKey("person.id", ondelete="CASCADE"), primary_key=True),
)


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
    __table_args__ = (UniqueConstraint("owner_id", "name", "is_tour", name="uq_owner_keyword_name"),)


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
    jobs = relationship("Job", foreign_keys="Job.source_aggregator_id", back_populates="source_aggregator")
    job_applications = relationship(
        "Job", foreign_keys="Job.application_aggregator_id", back_populates="application_aggregator"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("owner_id", "name", "is_tour", name="uq_owner_aggregator_name"),)


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
    jobs = relationship("Job", back_populates="company", foreign_keys="[Job.company_id]")
    persons = relationship("Person", back_populates="company")
    speculative_applications = relationship("SpeculativeApplication", back_populates="company")
    recruited_jobs = relationship(
        "Job", back_populates="recruitment_company", foreign_keys="[Job.recruitment_company_id]"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("owner_id", "name", "is_tour", name="uq_owner_company_name"),)


class Geolocation(Base, CommonBase):
    """Cache for geocoded location data to avoid redundant API calls.

    Attributes:
    -----------
    - `query` (str, unique): The location query string used for geocoding
    - `latitude` (float): Latitude coordinate
    - `longitude` (float): Longitude coordinate
    - `postcode` (str, optional): Postcode of the location
    - `city` (str, optional): City of the location
    - `country` (str, optional): Country of the location"""

    query = Column(String, nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)
    postcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)


class File(Owned, Base):
    """Represents files uploaded by the users.

    Attributes:
    -----------
    - `filename` (str): Name of the file.
    - `content` (bytes): Content of the file.
    - `type` (str): MIME type of the file.
    - `size` (int): Size of the file in bytes.
    - `file_type` (str): Semantic category of the file (e.g. 'cv', 'cover_letter').
    - `content_hash` (str): hashed content of the file."""

    filename = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=True)
    content_hash = Column(String, nullable=True, index=True)


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
    - `is_recruiter` (bool): Indicates whether the person is a recruiter.
    - `name` (str): Computed property combining first and last name.

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
    is_recruiter = Column(Boolean, nullable=False, server_default=expression.false())

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    company = relationship("Company", back_populates="persons")
    interviews = relationship("Interview", secondary=interview_interviewer_mapping, back_populates="interviewers")
    jobs = relationship("Job", secondary=job_contact_mapping, back_populates="contacts")
    speculative_applications = relationship(
        "SpeculativeApplication", secondary=speculative_application_contact_mapping, back_populates="contacts"
    )
    recruited_jobs = relationship("Job", back_populates="recruiter")

    @hybrid_property
    def name(self) -> str:
        """Computed property that combines the first and last name"""

        return f"{self.first_name} {self.last_name}"


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
    - `source_type` (str): Type of source used to post the job (e.g. job board, company website, etc.).
    - `followup_snooze_datetime` (datetime, optional): Date and time to snooze follow-up reminders.
    - `attendance_type` (str, optional): Type of attendance offered for the job (on-site, remote, hybrid).
    - `application_date` (datetime, optional): Date when the application was submitted.
    - `application_url` (str, optional): URL used to submit the application.
    - `application_status` (str, optional): Current status of the job application
    - `applied_via` (str, optional): Method used to apply for the job.
    - `application_note` (str, optional): Additional note about the job application.
    - `location` (str, optional): Free-text location string for the job.

    Foreign keys:
    -------------
    - `geolocation_id` (int, optional): Identifier for the geolocation derived from the location string.
    - `company_id` (int, optional): Identifier for the company offering the job.
    - `duplicate_id` (int, optional): Identifier for a duplicate job posting.
    - `source_aggregator_id` (int, optional): Identifier for the aggregator website where the job was posted.
    - `application_aggregator_id` (int, optional): Identifier for the aggregator website used to apply for the job.
    - `cv_id` (int, optional): Identifier for the CV file used in the job application.
    - `cover_letter_id` (int, optional): Identifier for the cover letter file used in the job application.

    Relationships:
    --------------
    - `company` (Company): Company object associated with the job posting.
    - `geolocation` (Geolocation): Geolocation object derived from the location string.
    - `keywords` (list of Keyword): List of keywords associated with the job posting.
    - `contacts` (list of Person): List of people linked to the company that may be interested in the job posting.
    - `source_aggregator` (Aggregator): Source of the job posting (e.g. LinkedIn, Indeed, etc.).
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
    source_type = Column(String, nullable=True)
    location = Column(String, nullable=True)

    is_favourite = Column(Boolean, nullable=False, server_default=expression.false())

    # Application-specific fields
    application_date = Column(TIMESTAMP(timezone=True), nullable=True)
    application_url = Column(String, nullable=True)
    application_status = Column(String, nullable=True)
    applied_via = Column(String, nullable=True)
    application_note = Column(String, nullable=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)
    geolocation_id = Column(Integer, ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True, index=True)
    duplicate_id = Column(Integer, ForeignKey("job.id", ondelete="SET NULL"), nullable=True, index=True)
    source_aggregator_id = Column(Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True, index=True)
    application_aggregator_id = Column(
        Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True, index=True
    )
    scraped_job_id = Column(Integer, ForeignKey("scraped_job.id", ondelete="SET NULL"), nullable=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("person.id", ondelete="SET NULL"), nullable=True, index=True)
    recruitment_company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)
    cv_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)
    cover_letter_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    company = relationship("Company", back_populates="jobs", foreign_keys=[company_id])
    geolocation = relationship("Geolocation", foreign_keys=[geolocation_id])
    keywords = relationship("Keyword", secondary=job_keyword_mapping, back_populates="jobs", lazy="selectin")
    contacts = relationship("Person", secondary=job_contact_mapping, back_populates="jobs", lazy="selectin")
    source_aggregator = relationship("Aggregator", foreign_keys=[source_aggregator_id], back_populates="jobs")
    interviews = relationship("Interview", back_populates="job")
    updates = relationship("JobApplicationUpdate", back_populates="job")
    application_aggregator = relationship(
        "Aggregator", foreign_keys=[application_aggregator_id], back_populates="job_applications"
    )
    recruiter = relationship("Person", foreign_keys=[recruiter_id], back_populates="recruited_jobs")
    recruitment_company = relationship(
        "Company", foreign_keys=[recruitment_company_id], back_populates="recruited_jobs"
    )
    application_cv = relationship("File", foreign_keys=[cv_id], lazy="select")
    application_cover_letter = relationship("File", foreign_keys=[cover_letter_id], lazy="select")
    scraped_job = relationship("ScrapedJob", foreign_keys=[scraped_job_id], lazy="select")

    @hybrid_property
    def has_application(self) -> bool:
        """True if any application field is populated."""
        return any([self.application_status, self.application_date, self.applied_via, self.application_url])

    @has_application.expression
    def has_application(cls):
        """True if any application field is populated for SQL queries"""
        return (
            cls.application_status.isnot(None)
            | cls.application_date.isnot(None)
            | cls.applied_via.isnot(None)
            | cls.application_url.isnot(None)
        )

    @hybrid_property
    def has_active_application(self) -> bool:
        """True if there is an application and it has not been rejected or withdrawn."""
        return self.has_application and self.application_status not in ("rejected", "withdrawn")

    @has_active_application.expression
    def has_active_application(cls):
        """True if there is an application, and it has not been rejected or withdrawn for SQL queries."""
        return cls.has_application & cls.application_status.notin_(("rejected", "withdrawn"))

    @hybrid_property
    def has_open_application(self) -> bool:
        """True if there is an application that is not closed (not rejected, withdrawn, or offered)."""
        return self.has_application and self.application_status not in ("rejected", "withdrawn", "offer")

    @has_open_application.expression
    def has_open_application(cls):
        """True if there is an application that is not closed for SQL queries."""
        return cls.has_application & cls.application_status.notin_(("rejected", "withdrawn", "offer"))

    __table_args__ = (
        CheckConstraint("personal_rating >= 1 AND personal_rating <= 5", name=f"valid_rating_range"),
        CheckConstraint("salary_min <= salary_max", name=f"valid_salary_range"),
        CheckConstraint("attendance_type IN ('on-site', 'remote', 'hybrid')", name="valid_attendance_type_values"),
        CheckConstraint(
            "application_status IN ('applied', 'interview', 'offer', 'rejected', 'withdrawn')",
            name="valid_application_status_values",
        ),
        CheckConstraint(
            "applied_via IN ('aggregator', 'email', 'company_website', 'phone', 'other')",
            name="valid_applied_via_values",
        ),
    )


class Interview(Owned, Base):
    """Represents interviews for job applications.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the interview.
    - `type` (str): Type of the interview (HR, technical, management, ...)
    - `note` (str, optional): Additional notes or comments about the interview.
    - `attendance_type` (str, optional): The attendance type of the interview (on-site, remote).
    - `location` (str, optional): The location of the interview.

    Foreign keys:
    -------------
    - `geolocation_id` (int, optional): Identifier for the geolocation derived from the location string.
    - `job_id` (int): Identifier for the job application associated with the interview.

    Relationships:
    --------------
    - `job` (Job): Job object related to the interview.
    - `interviewers` (list of Person): List of people who participated in the interview.
    - `geolocation` (Geolocation): Geolocation object derived from the location string.

    Constraints:
    ------------
    - `attendance_type` must be one of 'on-site' or 'remote' if provided."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    type = Column(String, nullable=False)
    note = Column(String, nullable=True)
    attendance_type = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Foreign keys
    geolocation_id = Column(Integer, ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True, index=True)
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    geolocation = relationship("Geolocation", foreign_keys=[geolocation_id])
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
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    job = relationship("Job", back_populates="updates")

    __table_args__ = (CheckConstraint("type IN ('received', 'sent')", name="valid_update_type_values"),)


class SpeculativeApplication(Owned, Base):
    """Represents a speculative application.

    Attributes:
    -----------
    - `date` (datetime, optional): The date and time of the application.
    - `note` (str, optional): Additional notes or comments about the application.
    - `contact_email` (str, optional): Email address used for the application.

    Foreign keys:
    -------------
    - `company_id` (int): Identifier for the company associated with the application.

    Relationships:
    --------------
    - `company` (Company): Company object related to the application.
    - `contact` (Person): Persons object related to the application."""

    date = Column(TIMESTAMP(timezone=True), nullable=True)
    note = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="speculative_applications")
    contacts = relationship(
        "Person",
        secondary=speculative_application_contact_mapping,
        back_populates="speculative_applications",
        lazy="selectin",
    )
