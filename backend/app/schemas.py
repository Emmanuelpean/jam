"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


def serialize_relationships(value) -> list[int]:
    """Serialize relationships to list of IDs"""
    if not value:
        return []
    if isinstance(value[0], int):
        return value
    return [item.id for item in value]


class Out(BaseModel):
    """Base model for all output schemas"""

    id: int
    created_at: datetime
    modified_at: datetime


class OwnedOut(Out):
    """Base model for all output schemas owned by a user"""

    owner_id: int


# ------------------------------------------------------- SETTINGS ------------------------------------------------------


class SettingCreate(BaseModel):
    """Setting create schema"""

    name: str
    value: str
    description: str | None = None
    is_active: bool = True


class SettingOut(SettingCreate, Out):
    """Setting output schema"""

    pass


class SettingUpdate(SettingCreate):
    """Keyword update schema"""

    name: str | None = None
    value: str | None = None


# -------------------------------------------------------- USER --------------------------------------------------------


class UserCreate(BaseModel):
    """User create schema"""

    password: str
    email: EmailStr


class UserOut(Out):
    """User output schema"""

    email: EmailStr
    theme: str
    is_active: bool = True
    is_admin: bool = False
    last_login: datetime | None = None
    chase_threshold: int
    deadline_threshold: int
    update_limit: int
    toast_active: bool


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""

    current_password: str | None = None
    email: EmailStr | None = None
    theme: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    last_login: datetime | None = None
    chase_threshold: int | None = None
    deadline_threshold: int | None = None
    update_limit: int | None = None
    toast_active: bool = False


# -------------------------------------------------------- TOKEN -------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


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


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class LocationCreate(BaseModel):
    """Location create schema"""

    postcode: str | None = None
    city: str | None = None
    country: str | None = None


class LocationOut(LocationCreate, OwnedOut):
    """Location output schema with job and interview data"""

    name: str | None = None
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
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    role: str | None = None

    # Foreign keys
    company_id: int | None = None


class PersonOut(PersonCreate, OwnedOut):
    """Person out schema with job data and bare interview data"""

    interviews: list[OwnedOut] = []
    jobs: list[OwnedOut] = []
    name: str | None = None
    name_company: str | None = None


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
    name: str

    @field_validator("keywords", "contacts", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialize_relationships(value)


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
        return serialize_relationships(value)


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
