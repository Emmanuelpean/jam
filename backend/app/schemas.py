"""Schemas for the JAM database"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Out(BaseModel):
    id: int
    created_at: datetime
    modified_at: datetime
    owner_id: int


# -------------------------------------------------------- USER --------------------------------------------------------


class UserCreate(BaseModel):
    password: str
    email: EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    modified_at: datetime
    theme: str
    is_admin: bool | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    theme: str | None = None
    password: str | None = None
    is_admin: bool | None = None


# -------------------------------------------------------- TOKEN -------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class Company(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class CompanyOut(Company, Out):
    pass


class CompanyUpdate(Company):
    name: str | None = None


# ------------------------------------------------------- KEYWORD ------------------------------------------------------


class Keyword(BaseModel):
    name: str


class KeywordOut(Keyword, Out):
    pass


class KeywordUpdate(Keyword):
    name: str | None = None


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class Aggregator(BaseModel):
    name: str
    url: str | None = None
    # jobs: list[int] | None = None
    # job_applications: list[int] | None = None


class AggregatorOut(Aggregator, Out):
    pass


class AggregatorUpdate(Aggregator):
    name: str | None = None


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class Location(BaseModel):
    postcode: str | None = None
    city: str | None = None
    country: str | None = None
    remote: bool = False


class LocationOut(Location, Out):
    name: str | None = None


class LocationUpdate(Location):
    pass


# -------------------------------------------------------- FILES -------------------------------------------------------


class File(BaseModel):
    filename: str
    type: str
    content: str
    size: int


class FileOut(File, Out):
    pass


class FileUpdate(File):
    filename: str | None = None
    type: str | None = None
    content: str | None = None
    size: int | None = None


# ------------------------------------------------------- PERSON -------------------------------------------------------


class Person(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    role: str | None = None
    company_id: int | None = None


# Simple person schema without interviews/jobs to avoid circular reference
class PersonSimple(Person, Out):
    company: CompanyOut | None = None
    name: str | None = None


class PersonOut(Person, Out):
    company: CompanyOut | None = None
    interviews: list["InterviewSimple"] = []
    jobs: list["JobSimple"] = []
    name: str | None = None


class PersonUpdate(Person):
    first_name: str | None = None
    last_name: str | None = None
    company_id: int | None = None


# --------------------------------------------------------- JOB --------------------------------------------------------


class Job(BaseModel):
    title: str
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    personal_rating: int | None = None
    url: str | None = None
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None
    note: str | None = None
    keywords: list[int] = []
    contacts: list[int] = []
    deadline: datetime | None = None
    source_id: int | None = None


# Simple job schema without job_application/contacts to avoid circular reference
class JobSimple(Job, Out):
    company: CompanyOut | None = None
    location: LocationOut | None = None
    keywords: list[KeywordOut] = []
    contacts: list[PersonSimple] = []
    name: str | None = None
    source: AggregatorOut | None = None


class JobOut(Job, Out):
    company: CompanyOut | None = None
    location: LocationOut | None = None
    keywords: list[KeywordOut] = []
    job_application: Optional["JobApplicationOut"] = None
    contacts: list[PersonSimple] = []
    name: str | None = None
    source: AggregatorOut | None = None


class JobUpdate(Job):
    title: str | None = None


# --------------------------------------------------- JOB APPLICATION --------------------------------------------------


class JobApplication(BaseModel):
    date: datetime
    url: str | None = None
    job_id: int
    status: str
    note: str | None = None
    applied_via: str | None = None
    aggregator_id: int | None = None
    cv_id: int | None = None
    cover_letter_id: int | None = None


class JobApplicationOut(JobApplication, Out):
    job: JobSimple | None = None
    aggregator: AggregatorOut | None = None
    interviews: list["InterviewSimple"] = []
    cv: FileOut | None = None
    cover_letter: FileOut | None = None


class JobApplicationSimple(JobApplication, Out):
    job: JobSimple | None = None
    aggregator: AggregatorOut | None = None
    cv: FileOut | None = None
    cover_letter: FileOut | None = None


class JobApplicationUpdate(JobApplication):
    date: datetime | None = None
    job_id: int | None = None
    status: str | None = None


# ------------------------------------------------------ INTERVIEW -----------------------------------------------------


class Interview(BaseModel):
    date: datetime
    location_id: int | None = None
    job_application_id: int
    note: str | None = None
    type: str | None = None
    interviewers: list[int] | None = None


class InterviewSimple(Interview, Out):
    location: LocationOut | None = None
    interviewers: list["PersonSimple"] = []


class InterviewOut(Interview, Out):
    location: LocationOut | None = None
    interviewers: list["PersonSimple"] = []
    job_application: JobApplicationSimple | None = None


class InterviewUpdate(Interview):
    date: datetime | None = None
    job_application_id: int | None = None


# ----------------------------------------------- JOB APPLICATION UPDATE -----------------------------------------------


class JobApplicationUpdateIn(BaseModel):
    date: datetime
    job_application_id: int
    note: str | None = None
    received: bool = False


class JobApplicationUpdateOut(JobApplicationUpdateIn, Out):
    job_application: JobApplicationOut | None = None


class JobApplicationUpdateUpdate(JobApplicationUpdateIn):
    date: datetime | None = None
    job_application_id: int | None = None
