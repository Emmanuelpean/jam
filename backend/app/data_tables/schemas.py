"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.base_schemas import OwnedOut, EmailField, serialise_relationships, OwnedCreate


# ------------------------------------------------------- KEYWORD ------------------------------------------------------


class KeywordCreate(OwnedCreate):
    """Keyword create schema"""

    name: str = Field(max_length=255, description="Keyword name")


class KeywordOut(KeywordCreate, OwnedOut):
    """Keyword output schema with full job data"""

    jobs: list[OwnedOut] = []


class KeywordUpdate(KeywordCreate):
    """Keyword update schema"""

    name: str | None = None


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class AggregatorCreate(OwnedCreate):
    """Aggregator create schema"""

    name: str = Field(max_length=255)
    url: str | None = Field(default=None, max_length=2048)


class AggregatorOut(AggregatorCreate, OwnedOut):
    """Aggregator output schema with full job data and job applications"""

    jobs: list[OwnedOut] = []
    job_applications: list[OwnedOut] = []


class AggregatorUpdate(AggregatorCreate):
    """Aggregator update schema"""

    name: str | None = None


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class CompanyCreate(OwnedCreate):
    """Company create schema"""

    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    url: str | None = Field(default=None, max_length=2048)


class CompanyOut(CompanyCreate, OwnedOut):
    """Company output schema with job data and individuals"""

    jobs: list[OwnedOut] = []
    persons: list[OwnedOut] = []
    recruited_jobs: list[OwnedOut] = []


class CompanyUpdate(CompanyCreate):
    """Company update schema"""

    name: str | None = None


# ------------------------------------------------------ GEOLOCATION ------------------------------------------------------


class GeolocationOut(BaseModel):
    """Geolocation output schema"""

    query: str
    latitude: float | None = None
    longitude: float | None = None
    postcode: str | None = None
    city: str | None = None
    country: str | None = None
    formatted_address: str | None = None


# -------------------------------------------------------- FILES -------------------------------------------------------


class FileCreate(OwnedCreate):
    """File create schema"""

    filename: str = Field(max_length=500)
    type: str = Field(max_length=100)
    content: str
    size: int
    file_type: str | None = Field(default=None, max_length=50)


class FileMetadataOut(OwnedOut):
    """File metadata output schema — excludes file content for use in related entities"""

    filename: str
    type: str
    size: int
    file_type: str | None = None


class FileOut(FileCreate, OwnedOut):
    """File output schema"""

    pass


class FileUpdate(FileCreate):
    """File update schema"""

    filename: str | None = None
    type: str | None = None
    content: str | None = None
    size: int | None = None


# ------------------------------------------------------- PERSON -------------------------------------------------------


class PersonCreate(OwnedCreate):
    """Person create schema"""

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailField | None = None
    phone: str | None = Field(default=None, max_length=30)
    linkedin_url: str | None = Field(default=None, max_length=2048)
    role: str | None = Field(default=None, max_length=255)
    is_recruiter: bool = False

    # Foreign keys
    company_id: int | None = None


class PersonOut(PersonCreate, OwnedOut):
    """Person out schema with job data and bare interview data"""

    interviews: list[OwnedOut] = []
    jobs: list[OwnedOut] = []
    recruited_jobs: list[OwnedOut] = []
    name: str | None = None


class PersonUpdate(PersonCreate):
    """Person update schema"""

    first_name: str | None = None
    last_name: str | None = None


# --------------------------------------------------------- JOB --------------------------------------------------------


class JobCreate(OwnedCreate):
    """Job create schema"""

    title: str = Field(max_length=255)
    is_favourite: bool = False
    description: str | None = Field(default=None, max_length=50000)
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = Field(default=None, max_length=10)
    personal_rating: int | None = None
    url: str | None = Field(default=None, max_length=2048)
    deadline: datetime | None = None
    note: str | None = Field(default=None, max_length=10000)
    attendance_type: str | None = Field(default=None, max_length=100)
    application_date: datetime | None = None
    application_url: str | None = Field(default=None, max_length=2048)
    application_status: str | None = Field(default=None, max_length=100)
    application_note: str | None = Field(default=None, max_length=10000)
    applied_via: str | None = Field(default=None, max_length=255)
    source_type: str | None = Field(default=None, max_length=100)
    followup_snooze_datetime: datetime | None = None
    location: str | None = Field(default=None, max_length=500)

    # Foreign keys
    company_id: int | None = None
    duplicate_id: int | None = None
    source_aggregator_id: int | None = None
    application_aggregator_id: int | None = None
    recruiter_id: int | None = None
    recruitment_company_id: int | None = None
    scraped_job_id: int | None = None
    cv_id: int | None = None
    cover_letter_id: int | None = None
    keywords: list[int] = []
    contacts: list[int] = []


class JobOut(JobCreate, OwnedOut):
    """Job output schema with IDs of related entities"""

    keywords: list[int] = []
    contacts: list[int] = []
    interviews: list[OwnedOut] = []
    updates: list[OwnedOut] = []
    has_application: bool = False
    has_active_application: bool = False
    has_open_application: bool = False
    geolocation: GeolocationOut | None = None
    application_cv: FileMetadataOut | None = None
    application_cover_letter: FileMetadataOut | None = None

    @field_validator("keywords", "contacts", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class JobUpdate(JobCreate):
    """Job update schema"""

    title: str | None = None


# ------------------------------------------------------ INTERVIEW -----------------------------------------------------


class InterviewCreate(OwnedCreate):
    """Interview create schema"""

    date: datetime
    type: str = Field(max_length=100)
    job_id: int
    attendance_type: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=10000)
    interviewers: list[int] | None = None


class InterviewOut(InterviewCreate, OwnedOut):
    """Interview output with bare location and person data, and job data"""

    interviewers: list[int] = []
    geolocation: GeolocationOut | None = None

    @field_validator("interviewers", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class InterviewUpdate(InterviewCreate):
    """Interview update schema"""

    date: datetime | None = None
    type: str | None = None
    job_id: int | None = None


# ----------------------------------------------- JOB APPLICATION UPDATE -----------------------------------------------


class JobApplicationUpdateCreate(OwnedCreate):
    """Job Application Update create schema"""

    date: datetime
    type: str = Field(max_length=100)
    job_id: int
    note: str | None = Field(default=None, max_length=10000)


class JobApplicationUpdateOut(JobApplicationUpdateCreate, OwnedOut):
    """Job Application Update output schema with job data"""

    pass


class JobApplicationUpdateUpdate(JobApplicationUpdateCreate):
    """Job Application Update update schema"""

    date: datetime | None = None
    type: str | None = None
    job_id: int | None = None


# ----------------------------------------------- SPECULATIVE APPLICATION ----------------------------------------------


class SpeculativeApplicationCreate(OwnedCreate):
    """Speculative application create schema"""

    date: datetime | None = None
    note: str | None = Field(default=None, max_length=10000)
    contact_email: str | None = Field(default=None, max_length=254)

    # Foreign keys
    company_id: int
    contacts: list[int] = []


class SpeculativeApplicationOut(SpeculativeApplicationCreate, OwnedOut):
    """Speculative application output schema"""

    @field_validator("contacts", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class SpeculativeApplicationUpdate(SpeculativeApplicationCreate):
    """Speculative application update schema"""

    company_id: int | None = None
