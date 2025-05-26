"""
This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`.

Key Classes:
------------
1. **CommonBase**:
   - A shared base class for all models except User, providing common attributes such as `id`, `created_at`, and `owner_id`.
   - Automatically sets the table name to the lowercase name of the model class.

2. **User**:
   - Represents the users of the system with details such as `username`, `email` and `password` attributes.

3. **Person**, **Company**, and **Job**:
   - Provide the structure for storing information about individuals, companies, and job postings, with relationships
     between them to enable queries on dependencies (e.g. employees in a company).

4. **Location**:
   - Stores information about the geographic locations associated with jobs or interviews, supporting fields like
     `postcode`, `city`, `country`, and whether the job supports remote work.

5. **Website**:
   - Defines records to track the associated websites of a company, including details about their `name` and `url`.

6. **Interview**:
   - Represents job application events, linking jobs, locations, and persons involved.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, TIMESTAMP, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .database import Base


class CommonBase(object):
    """Common base class for all models except user"""

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
    - `username` (str): Unique identifier for the user.
    - `email` (str): User's email address (must be unique).
    - `password` (str): Encrypted password for authentication."""

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
    - `company_id` (int): Foreign key linking the person to a company.
    - `company` (Company): Relationship to access the associated company."""

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    company = relationship("Company")


class Company(CommonBase, Base):
    """Represents a company or organization.

    Attributes:
    -----------
    - `name` (str): Name of the company.
    - `website_id` (int): Foreign key linking to the company's website.
    - `website` (Website): Relationship to access the associated website.
    """

    name = Column(String, nullable=False)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    website = relationship("Website")


class Job(CommonBase, Base):
    """Job table"""

    title = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    company = relationship("Company")
    salary_min = Column(Float)
    salary_max = Column(Float)
    description = Column(String)
    location = Column(String)
    personal_rating = Column(Integer)
    url = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")


class Location(CommonBase, Base):
    """Location table"""

    postcode = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    remote = Column(Boolean, nullable=False)


class Website(CommonBase, Base):
    """Website table"""

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)


class Interview(CommonBase, Base):
    """Interview table"""

    date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    location = relationship("Location")
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    job = relationship("Job")
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    person = relationship("Person")
