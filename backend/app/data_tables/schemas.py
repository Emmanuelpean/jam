"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.base_schemas import OwnedOut, EmailField, serialise_relationships, OwnedCreate, COLUMN_LIMITS
from app.config import settings

# ------------------------------------------------------- KEYWORD ------------------------------------------------------


class KeywordCreate(OwnedCreate):
    """Keyword create schema"""

    name: str = Field(max_length=COLUMN_LIMITS.name)


class KeywordOut(KeywordCreate, OwnedOut):
    """Keyword output schema with full job data"""

    pass


class KeywordUpdate(KeywordCreate):
    """Keyword update schema"""

    name: str | None = Field(default=None, max_length=COLUMN_LIMITS.name)


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class AggregatorCreate(OwnedCreate):
    """Aggregator create schema"""

    name: str = Field(max_length=COLUMN_LIMITS.name)
    url: str | None = Field(default=None, max_length=COLUMN_LIMITS.url)


class AggregatorOut(AggregatorCreate, OwnedOut):
    """Aggregator output schema with full job data and job applications"""

    pass


class AggregatorUpdate(AggregatorCreate):
    """Aggregator update schema"""

    name: str | None = Field(default=None, max_length=COLUMN_LIMITS.name)


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class CompanyCreate(OwnedCreate):
    """Company create schema"""

    name: str = Field(max_length=COLUMN_LIMITS.name)
    description: str | None = Field(default=None, max_length=COLUMN_LIMITS.description)
    url: str | None = Field(default=None, max_length=COLUMN_LIMITS.url)


class CompanyOut(CompanyCreate, OwnedOut):
    """Company output schema with job data and individuals"""

    pass


class CompanyUpdate(CompanyCreate):
    """Company update schema"""

    name: str | None = Field(default=None, max_length=COLUMN_LIMITS.name)


# ------------------------------------------------------ GEOLOCATION ------------------------------------------------------


class GeolocationOut(BaseModel):
    """Geolocation output schema"""

    query: str
    latitude: float | None = None
    longitude: float | None = None
    postcode: str | None = None
    city: str | None = None
    country: str | None = None


# -------------------------------------------------------- FILES -------------------------------------------------------

# base64 overhead is 4/3; +200 for data URL prefix (e.g. "data:application/pdf;base64,")
FILE_CONTENT_MAX_LENGTH = int(settings.max_file_size_mb * 1024 * 1024 * 4 / 3) + 200


class FileCreate(OwnedCreate):
    """File create schema"""

    filename: str = Field(max_length=COLUMN_LIMITS.file_name)
    type: str = Field(max_length=COLUMN_LIMITS.file_mimetype)
    content: str = Field(max_length=FILE_CONTENT_MAX_LENGTH)
    size: int = Field(ge=0)
    file_type: str | None = Field(default=None, max_length=COLUMN_LIMITS.file_type)


class FileOut(OwnedOut):
    """File metadata output schema — excludes file content for use in related entities"""

    filename: str
    type: str
    size: int
    file_type: str | None


class FileWithContentOut(FileOut):
    """File output schema"""

    content: str


class FileUpdate(OwnedCreate):
    """File update schema — only the filename may be changed."""

    filename: str | None = Field(default=None, max_length=COLUMN_LIMITS.file_name)


# ------------------------------------------------------- PERSON -------------------------------------------------------


class PersonCreate(OwnedCreate):
    """Person create schema"""

    first_name: str = Field(max_length=COLUMN_LIMITS.first_name)
    last_name: str = Field(max_length=COLUMN_LIMITS.last_name)
    email: EmailField | None = None
    phone: str | None = Field(default=None, max_length=COLUMN_LIMITS.phone)
    linkedin_url: str | None = Field(default=None, max_length=COLUMN_LIMITS.url)
    role: str | None = Field(default=None, max_length=COLUMN_LIMITS.role)
    is_recruiter: bool = False

    # Foreign keys
    company_id: int | None = None


class PersonOut(PersonCreate, OwnedOut):
    """Person out schema with job data and bare interview data"""

    name: str | None


class PersonUpdate(PersonCreate):
    """Person update schema"""

    first_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.first_name)
    last_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.last_name)


# --------------------------------------------------------- JOB --------------------------------------------------------


class JobCreate(OwnedCreate):
    """Job create schema"""

    title: str = Field(max_length=COLUMN_LIMITS.job_title)
    is_favourite: bool = False
    description: str | None = Field(default=None, max_length=COLUMN_LIMITS.description)
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = Field(default=None, max_length=COLUMN_LIMITS.currency)
    personal_rating: int | None = None
    url: str | None = Field(default=None, max_length=COLUMN_LIMITS.url)
    deadline: datetime | None = None
    note: str | None = Field(default=None, max_length=COLUMN_LIMITS.note)
    attendance_type: str | None = Field(default=None, max_length=COLUMN_LIMITS.attendance_type)
    application_date: datetime | None = None
    application_url: str | None = Field(default=None, max_length=COLUMN_LIMITS.url)
    application_status: str | None = Field(default=None, max_length=COLUMN_LIMITS.application_status)
    application_note: str | None = Field(default=None, max_length=COLUMN_LIMITS.note)
    applied_via: str | None = Field(default=None, max_length=COLUMN_LIMITS.applied_via)
    source_type: str | None = Field(default=None, max_length=COLUMN_LIMITS.source_type)
    followup_snooze_datetime: datetime | None = None
    location: str | None = Field(default=None, max_length=COLUMN_LIMITS.location)

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

    has_application: bool = False
    has_active_application: bool = False
    has_open_application: bool = False
    geolocation: GeolocationOut | None = None

    @field_validator("keywords", "contacts", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class JobUpdate(JobCreate):
    """Job update schema"""

    title: str | None = Field(default=None, max_length=COLUMN_LIMITS.job_title)


# ------------------------------------------------------ INTERVIEW -----------------------------------------------------


class InterviewCreate(OwnedCreate):
    """Interview create schema"""

    date: datetime
    type: str = Field(max_length=COLUMN_LIMITS.interview_type)
    job_id: int
    attendance_type: str | None = Field(default=None, max_length=COLUMN_LIMITS.attendance_type)
    location: str | None = Field(default=None, max_length=COLUMN_LIMITS.location)
    note: str | None = Field(default=None, max_length=COLUMN_LIMITS.note)
    interviewers: list[int] | None = None


class InterviewOut(InterviewCreate, OwnedOut):
    """Interview output with bare location and person data, and job data"""

    geolocation: GeolocationOut | None = None

    @field_validator("interviewers", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class InterviewUpdate(InterviewCreate):
    """Interview update schema"""

    date: datetime | None = None
    type: str | None = Field(default=None, max_length=COLUMN_LIMITS.interview_type)
    job_id: int | None = None


# ----------------------------------------------- JOB APPLICATION UPDATE -----------------------------------------------


class JobApplicationUpdateCreate(OwnedCreate):
    """Job Application Update create schema"""

    date: datetime
    type: str = Field(max_length=COLUMN_LIMITS.update_type)
    job_id: int
    note: str | None = Field(default=None, max_length=COLUMN_LIMITS.note)


class JobApplicationUpdateOut(JobApplicationUpdateCreate, OwnedOut):
    """Job Application Update output schema with job data"""

    pass


class JobApplicationUpdateUpdate(JobApplicationUpdateCreate):
    """Job Application Update update schema"""

    date: datetime | None = None
    type: str | None = Field(default=None, max_length=COLUMN_LIMITS.update_type)
    job_id: int | None = None


# ----------------------------------------------- SPECULATIVE APPLICATION ----------------------------------------------


class SpeculativeApplicationCreate(OwnedCreate):
    """Speculative application create schema"""

    date: datetime | None = None
    note: str | None = Field(default=None, max_length=COLUMN_LIMITS.note)
    contact_email: EmailField | None = None
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
