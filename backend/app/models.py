"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, TIMESTAMP, text, CheckConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.database import Base


class CommonBase(object):
    """A base class that contains common attributes shared by multiple tables.

    Attributes:
    -----------
    - `id` (int): Primary key of the record.
    - `created_at` (datetime): The timestamp of when the record was created.
    - `owner_id` (int): Identifier for the owner of the record. Linked to the user table.
    """

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls) -> str:
        """Return the class name as table name"""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    modified_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), server_onupdate=text("now()"), nullable=False
    )
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)


class User(Base):
    """Represents the users of the application.

    Attributes:
    -----------
    - `id` (int): Primary key for the user.
    - `created_at` (datetime): The timestamp of when the user record was created.
    - `username` (str): Unique identifier for the user.
    - `password` (str): Encrypted password for authentication.
    - `email` (str): User's email address (must be unique)."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class Company(CommonBase, Base):
    """Represents a company or organisation.

    Attributes:
    -----------
    - `name` (str): Name of the company.
    - `description` (str, optional): Description or details about the company.
    - `url` (str, optional): Web link to the company's website."""

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)


class Keyword(CommonBase, Base):
    """Represents keywords associated with job postings.

    Attributes:
    -----------
    - `name` (str): The keyword name."""

    name = Column(String, nullable=False)


class Aggregator(CommonBase, Base):
    """Represents a website associated with an aggregator company (e.g. LinkedIn, Indeed).

    Attributes:
    -----------
    - `name` (str): The website's name.
    - `url` (str): The website's URL."""

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)


class Location(CommonBase, Base):
    """Represents geographical locations.

    Attributes:
    -----------
    - `postcode` (str, optional): Postcode of the location.
    - `city` (str, optional): City of the location.
    - `country` (str, optional): Country where the location resides.
    - `remote` (bool, optional): Indicates if the location is remote"""

    postcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    remote = Column(Boolean, nullable=True)  # TODO

    __table_args__ = (
        CheckConstraint(
            "postcode IS NOT NULL OR city IS NOT NULL OR country IS NOT NULL OR remote IS NOT NULL",
            name="at_least_one_location_field_required",
        ),
    )


class Person(CommonBase, Base):
    """Represents an individual linked to a company.

    Attributes:
    -----------
    - `first_name` (str): First name of the person.
    - `last_name` (str): Last name of the person.
    - `email` (str, optional): Email address of the person.
    - `phone` (str, optional): Phone number of the person.
    - `linkedin_url` (str, optional): LinkedIn profile URL of the person.
    - `company_id` (int): Foreign key linking the person to a company.
    - `company` (Company): Relationship to access the associated company."""

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=True)
    company = relationship("Company")


class Job(CommonBase, Base):
    """Represents job postings within the application.

    Attributes:
    -----------
    - `title` (str): The job title.
    - `description` (str, optional): Description or details about the job.
    - `salary_min` (float, optional): Minimum salary offered for the job.
    - `salary_max` (float, optional): Maximum salary offered for the job.
    - `url` (str, optional): Web link to the job posting.
    - `personal_rating` (int, optional): Personalized rating given to the job.
    - `company_id` (int): Identifier for the company offering the job.
    - `company` (Company): Company object associated with the job posting.
    - `location_id` (int, optional): Identifier for the geographical location where the job is located.
    - `location` (Location): Location object associated with the job posting.
    - `duplicate_id` (int, optional): Identifier for a duplicate job posting."""

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    url = Column(String, nullable=True)
    personal_rating = Column(Integer, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=True)
    company = relationship("Company")
    location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"), nullable=True)
    location = relationship("Location")
    duplicate_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=True)


class Interview(CommonBase, Base):
    """Represents interviews for job applications.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the interview.
    - `location_id` (int): Identifier for the location of the interview.
    - `location` (Location): Location object related to the interview.
    - `job_id` (int): Identifier for the job associated with the interview.
    - `job` (Job): Job object related to the interview.
    - `note` (str, optional): Additional notes or comments about the interview."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"), nullable=False)
    location = relationship("Location")
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    job = relationship("Job")
    note = Column(String, nullable=True)


class JobApplication(CommonBase, Base):
    """Represents job applications for a person.

    Attributes:
    -----------
    - `date` (datetime): The date and time of the application.
    - `url` (str, optional): URL to the job application.
    - `job_id` (int): Identifier for the job associated with the application.
    - `job` (Job): Job object related to the application.
    - `rejected` (bool, optional): Indicates if the application was rejected.
    - `note` (str, optional): Additional notes or comments about the application."""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    url = Column(String, nullable=True)
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    job = relationship("Job")
    rejected = Column(Boolean, nullable=True)
    note = Column(String, nullable=True)
