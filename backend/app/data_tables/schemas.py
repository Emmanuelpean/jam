"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.base_schemas import OwnedOut, EmailField, serialise_relationships


# ------------------------------------------------------- KEYWORD ------------------------------------------------------


class KeywordCreate(BaseModel):
    """Keyword create schema"""

    name: str


class KeywordOut(KeywordCreate, OwnedOut):
    """Keyword output schema with full job data"""

    jobs: list[OwnedOut] = []


class KeywordUpdate(KeywordCreate):
    """Keyword update schema"""

    name: str | None = None


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class AggregatorCreate(BaseModel):
    """Aggregator create schema"""

    name: str
    url: str | None = None


class AggregatorOut(AggregatorCreate, OwnedOut):
    """Aggregator output schema with full job data and job applications"""

    jobs: list[OwnedOut] = []
    job_applications: list[OwnedOut] = []


class AggregatorUpdate(AggregatorCreate):
    """Aggregator update schema"""

    name: str | None = None


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class CompanyCreate(BaseModel):
    """Company create schema"""

    name: str
    description: str | None = None
    url: str | None = None


class CompanyOut(CompanyCreate, OwnedOut):
    """Company output schema with job data and individuals"""

    jobs: list[OwnedOut] = []
    persons: list[OwnedOut] = []


class CompanyUpdate(CompanyCreate):
    """Company update schema"""

    name: str | None = None


# ------------------------------------------------------ GEOLOCATION ------------------------------------------------------


class GeolocationOut(BaseModel):
    """Geolocation output schema"""

    query: str
    latitude: float
    longitude: float
    formatted_address: str | None = None


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class LocationCreate(BaseModel):
    """Location create schema"""

    postcode: str | None = None
    city: str | None = None
    country: str | None = None


class LocationOut(LocationCreate, OwnedOut):
    """Location output schema with job and interview data"""

    name: str | None = None
    geolocation: GeolocationOut | None = None
    jobs: list[OwnedOut] = []
    interviews: list[OwnedOut] = []


class LocationUpdate(LocationCreate):
    """Location update schema"""

    pass


# -------------------------------------------------------- FILES -------------------------------------------------------


class FileCreate(BaseModel):
    """File create schema"""

    filename: str
    type: str
    content: str
    size: int


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


class PersonCreate(BaseModel):
    """Person create schema"""

    first_name: str
    last_name: str
    email: EmailField | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    role: str | None = None
    is_recruiter: bool = False

    # Foreign keys
    company_id: int | None = None


class PersonOut(PersonCreate, OwnedOut):
    """Person out schema with job data and bare interview data"""

    interviews: list[OwnedOut] = []
    jobs: list[OwnedOut] = []
    name: str | None = None


class PersonUpdate(PersonCreate):
    """Person update schema"""

    first_name: str | None = None
    last_name: str | None = None


# --------------------------------------------------------- JOB --------------------------------------------------------


class JobCreate(BaseModel):
    """Job create schema"""

    title: str
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    personal_rating: int | None = None
    url: str | None = None
    deadline: datetime | None = None
    note: str | None = None
    attendance_type: str | None = None
    application_date: datetime | None = None
    application_url: str | None = None
    application_status: str | None = None
    application_note: str | None = None
    applied_via: str | None = None
    followup_snooze_datetime: datetime | None = None

    # Foreign keys
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None
    source_id: int | None = None
    application_aggregator_id: int | None = None
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

    @field_validator("keywords", "contacts", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class JobUpdate(JobCreate):
    """Job update schema"""

    title: str | None = None


# ------------------------------------------------------ INTERVIEW -----------------------------------------------------


class InterviewCreate(BaseModel):
    """Interview create schema"""

    date: datetime
    type: str
    job_id: int
    attendance_type: str | None = None
    location_id: int | None = None
    note: str | None = None
    interviewers: list[int] | None = None


class InterviewOut(InterviewCreate, OwnedOut):
    """Interview output with bare location and person data, and job data"""

    interviewers: list[int] = []

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


class JobApplicationUpdateCreate(BaseModel):
    """Job Application Update create schema"""

    date: datetime
    type: str
    job_id: int
    note: str | None = None


class JobApplicationUpdateOut(JobApplicationUpdateCreate, OwnedOut):
    """Job Application Update output schema with job data"""

    pass


class JobApplicationUpdateUpdate(JobApplicationUpdateCreate):
    """Job Application Update update schema"""

    date: datetime | None = None
    type: str | None = None
    job_id: int | None = None


# ----------------------------------------------- SPECULATIVE APPLICATION ----------------------------------------------


class SpeculativeApplicationCreate(BaseModel):
    """Speculative application create schema"""

    date: datetime | None = None
    note: str | None = None
    contact_email: str | None = None

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
