"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

import re

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
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.database import Base
from app.config import settings

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


class Settings(CommonBase, Base):
    """Represents the application settings

    Attributes:
    -----------
    - `quantity` (str): The name of the setting.
    - `value` (float): The value of the setting.
    - `description` (str): A description of the setting."""

    quantity = Column(String, nullable=False, unique=True)
    value = Column(Float, nullable=False)
    description = Column(String, nullable=False)


class User(CommonBase, Base):
    """Represents users of the application.

    Attributes:
    -----------
    - `password` (str): Encrypted password for authentication.
    - `email` (str): User's email address (must be unique).
    - `theme` (str): The theme of the application.
    - `is_admin` (bool): Indicates whether the user is an administrator.
    - `last_login` (datetime): The timestamp of the last login."""

    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    theme = Column(String, nullable=False, server_default="mixed-berry")
    is_admin = Column(Boolean, nullable=False, server_default=expression.false())
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(f"length(password) >= {settings.min_password_length}", name="minimum_password_length"),
    )


# -------------------------------------------------------- DATA --------------------------------------------------------


class Keyword(Owned, Base):
    """Represents keywords associated with job postings.

    Attributes:
    -----------
    - `name` (str): The keyword name.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the keyword."""

    name = Column(String, nullable=False)

    # Relationships
    jobs = relationship("Job", secondary=job_keyword_mapping, back_populates="keywords")


class Aggregator(Owned, Base):
    """Represents an aggregator website (e.g. LinkedIn, Indeed).

    Attributes:
    -----------
    - `name` (str): The website's name.
    - `url` (str): The website's URL.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the aggregator.
    - `job_applications` (list of JobApplication): List of job applications associated with the aggregator."""

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    jobs = relationship("Job", back_populates="source")
    job_applications = relationship("JobApplication", back_populates="aggregator")


class Company(Owned, Base):
    """Represents a company or organisation.

    Attributes:
    -----------
    - `name` (str): Name of the company.
    - `description` (str, optional): Description or details about the company.
    - `url` (str, optional): Web link to the company's website.

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the company.
    - `persons` (list of Person): List of people linked to the company."""

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="company")
    persons = relationship("Person", back_populates="company")


class Location(Owned, Base):
    """Represents geographical locations.

    Attributes:
    -----------
    - `postcode` (str, optional): Postcode of the location.
    - `city` (str, optional): City of the location.
    - `country` (str, optional): Country where the location resides.
    - `remote` (bool, optional): Indicates if the location is remote
    - `name` (str): Computed property combining city, country, and postcode

    Relationships:
    --------------
    - `jobs` (list of Job): List of jobs associated with the location.
    - `interviews` (list of Interview): List of interviews associated with the location."""

    postcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    remote = Column(Boolean, nullable=False, server_default=expression.false())

    # Relationships
    jobs = relationship("Job", back_populates="location")
    interviews = relationship("Interview", back_populates="location")

    @hybrid_property
    def name(self) -> str:
        """Computed property that combines city, country, and postcode into a readable location name"""

        if self.remote:
            return "Remote"

        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        if self.postcode:
            parts.append(self.postcode)

        return ", ".join(parts) if parts else "Unknown Location"

    __table_args__ = (
        CheckConstraint(
            "(postcode IS NOT NULL OR city IS NOT NULL OR country IS NOT NULL) OR remote = true",
            name=f"location_data_required_unless_remote",
        ),
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
    - `name` (str): Computed property combining the job title and company name.

    Foreign keys:
    -------------
    - `company_id` (int): Identifier for the company offering the job.
    - `location_id` (int, optional): Identifier for the geographical location where the job is located.
    - `duplicate_id` (int, optional): Identifier for a duplicate job posting.
    - `source_id` (int, optional): Identifier for the aggregator website where the job was posted.

    Relationships:
    --------------
    - `company` (Company): Company object associated with the job posting.
    - `location` (Location): Location object associated with the job posting.
    - `keywords` (list of Keyword): List of keywords associated with the job posting.
    - `job_application` (JobApplication): JobApplication object related to the job posting.
    - `contacts` (list of Person): List of people linked to the company that may be interested in the job posting.
    - `source` (Aggregator): Source of the job posting (e.g. LinkedIn, Indeed, etc.)."""

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    url = Column(String, nullable=True)
    personal_rating = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True)
    duplicate_id = Column(Integer, ForeignKey("job.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    location = relationship("Location", back_populates="jobs")
    keywords = relationship("Keyword", secondary=job_keyword_mapping, back_populates="jobs", lazy="selectin")
    job_application = relationship("JobApplication", back_populates="job", uselist=False)
    contacts = relationship("Person", secondary=job_contact_mapping, back_populates="jobs", lazy="selectin")
    source = relationship("Aggregator", back_populates="jobs")

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
    )


class JobApplication(Owned, Base):
    """Represents job applications.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the application.
    - `url` (str, optional): URL to the job application.
    - `status` (str): Status of the application (Applied, Interview, Rejected, etc.).
    - `applied_via` (str, optional): Method of application (email, phone, etc.).
    - `note` (str, optional): Additional notes or comments about the application.

    Foreign keys:
    -------------
    - `job_id` (int): Identifier for the job associated with the application.
    - `aggregator_id` (int, optional): Identifier for the aggregator website through which the application was made.
    - `cv_id` (int, optional): Identifier for the CV uploaded by the user.
    - `cover_letter_id` (int, optional): Identifier for the cover letter uploaded by the user.

    Relationships:
    --------------
    - `job` (Job): Job object related to the application.
    - `interviews` (list of Interview): List of interviews performed.
    - `aggregator` (Aggregator): Aggregator website through which the application was made.
    - `cv` (File): CV uploaded by the user.
    - `cover_letter` (File): Cover letter uploaded by the user.
    - `updates` (list of JobApplicationUpdate): List of updates made to the application."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    url = Column(String, nullable=True)
    status = Column(String, server_default="Applied", nullable=False)
    applied_via = Column(String, nullable=True)
    note = Column(String, nullable=True)

    # Foreign keys
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, unique=True)
    aggregator_id = Column(Integer, ForeignKey("aggregator.id", ondelete="SET NULL"), nullable=True, index=True)
    cv_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)
    cover_letter_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    job = relationship("Job", back_populates="job_application")
    interviews = relationship("Interview", back_populates="job_application")
    aggregator = relationship("Aggregator", back_populates="job_applications")
    cv = relationship("File", foreign_keys=[cv_id], lazy="select")
    cover_letter = relationship("File", foreign_keys=[cover_letter_id], lazy="select")
    updates = relationship("JobApplicationUpdate", back_populates="job_application")


class Interview(Owned, Base):
    """Represents interviews for job applications.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the interview.
    - `type` (str): Type of the interview (HR, technical, management, ...)
    - `note` (str, optional): Additional notes or comments about the interview.

    Foreign keys:
    -------------
    - `location_id` (int): Identifier for the location of the interview.
    - `job_application_id` (int): Identifier for the job application associated with the interview.

    Relationships:
    --------------
    - `job_application` (JobApplication): JobApplication object related to the interview.
    - `interviewers` (list of Person): List of people who participated in the interview.
    - `location` (Location): Location object related to the interview."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    type = Column(String, nullable=False)
    note = Column(String, nullable=True)

    # Foreign keys
    location_id = Column(Integer, ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True)
    job_application_id = Column(
        Integer, ForeignKey("job_application.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    location = relationship("Location", back_populates="interviews")
    job_application = relationship("JobApplication", back_populates="interviews")
    interviewers = relationship("Person", secondary=interview_interviewer_mapping, back_populates="interviews")


class JobApplicationUpdate(Owned, Base):
    """Represents an update to a job application.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the update.
    - `note` (str, optional): Additional notes or comments about the update.
    - `type` (str): The type of the update (received, sent).

    Foreign keys:
    -------------
    - job_application_id (int): Identifier for the job application associated with the update.

    Relationships:
    --------------
    - `job_application` (JobApplication): JobApplication object related to the update."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    note = Column(String, nullable=True)
    type = Column(String, nullable=False)

    # Foreign keys
    job_application_id = Column(Integer, ForeignKey("job_application.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    job_application = relationship("JobApplication", back_populates="updates")
