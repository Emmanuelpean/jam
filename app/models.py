"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`.

Key Classes:
------------
1. **CommonBase**: Base class with common attributes shared by multiple tables.
2. **User**: Represents application users and their credentials.
3. **Person**: Represents individual persons and their contact information.
4. **Company**: Stores information about companies.
5. **Job**: Represents job postings, their details, and associated companies.
6. **Location**: Defines geographic locations, including city and country.
7. **AggregatorWebsite**: Represents job aggregation platforms with their metadata.
8. **Interview**: Tracks interviews, including date, location, job, and person details.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, TIMESTAMP, text, CheckConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .database import Base


class CommonBase(object):
    """A base class that contains common attributes shared by multiple tables.
    Attributes:
    - `id` (int): Primary key of the record.
    - `created_at` (datetime): The timestamp of when the record was created.
    - `owner_id` (int): Identifier for the owner of the record. Linked to the user table."""

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls) -> str:
        """Return the class name as table name"""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)


class User(Base):
    """Represents the users of the application.

    Attributes:
    -----------
    - `id` (int): Primary key for the user.
    - `created_at` (datetime): The timestamp of when the user record was created.
    - `username` (str): Unique identifier for the user.
    - `email` (str): User's email address (must be unique).
    - `password` (str): Encrypted password for authentication."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    username = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class Person(CommonBase, Base):
    """Represents an individual linked to a company.

    Attributes:
    -----------
    - `first_name` (str): First name of the person.
    - `last_name` (str): Last name of the person.
    - `email` (str, optional): Email address of the person.
    - `phone` (str, optional): Phone number of the person.
    - `company_id` (int): Foreign key linking the person to a company.
    - `company` (Company): Relationship to access the associated company."""

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    company = relationship("Company")


class Company(CommonBase, Base):
    """Represents a company or organization.

    Attributes:
    -----------
    - `name` (str): Name of the company.
    - `description` (str, optional): Description or details about the company.
    - `url` (str, optional): Web link to the company's website."""

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)


class Job(CommonBase, Base):
    """Represents job postings within the application.

    Attributes:
    -----------
    - `title` (str): The job title.
    - `company_id` (int): Identifier for the company offering the job.
    - `company` (Company): Company object associated with the job posting.
    - `salary_min` (float, optional): Minimum salary offered for the job.
    - `salary_max` (float, optional): Maximum salary offered for the job.
    - `description` (str, optional): Description or details about the job.
    - `location_id` (int, optional): Identifier for the geographical location where the job is located.
    - `location` (Location): Location object associated with the job posting.
    - `personal_rating` (int, optional): Personalized rating given to the job.
    - `url` (str, optional): Web link to the job posting."""

    title = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=True)
    company = relationship("Company")
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"), nullable=True)
    location = relationship("Location")
    personal_rating = Column(Integer, CheckConstraint("personal_rating >= 0 AND personal_rating <= 10"), nullable=True)
    url = Column(String, nullable=True)


class Location(CommonBase, Base):
    """Represents geographical locations.

    Attributes:
    -----------
    - `postcode` (str, optional): Postal or ZIP code of the location.
    - `city` (str, optional): City of the location.
    - `country` (str, optional): Country where the location resides.
    - `remote` (bool, optional): Indicates if the location is remote"""

    postcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    remote = Column(Boolean, nullable=True)


class AggregatorWebsite(CommonBase, Base):
    """Represents a website associated with an aggregator company (e.g. LinkedIn, Indeed).

    Attributes:
    -----------
    - `name` (str): The website's name.
    - `url` (str): The website's URL."""

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)


#
# class Interview(CommonBase, Base):  # TODO to finish
#     """Represents interviews for job applications.
#
#     Attributes:
#     -----------
#     - `date` (datetime): The date and time of the interview.
#     - `location_id` (int): Identifier for the location of the interview.
#     - `location` (Location): Location object related to the interview.
#     - `job_id` (int): Identifier for the job associated with the interview.
#     - `job` (Job): Job object related to the interview.
#     - `person_id` (int): Identifier for the person attending the interview.
#     - `person` (Person): Person object who is attending the interview.
#     """
#
#     date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
#     location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"), nullable=False)
#     location = relationship("Location")
#     job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
#     job = relationship("Job")
#     person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
#     person = relationship("Person")
