"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime, UTC
from typing import Optional

from pydantic import BaseModel, EmailStr, computed_field


class Out(BaseModel):
    """Base model for all output schemas"""

    id: int
    created_at: datetime
    modified_at: datetime


class OwnedOut(Out):
    """Base model for all output schemas owned by a user"""

    owner_id: int


# -------------------------------------------------------- USER --------------------------------------------------------


class UserCreate(BaseModel):
    password: str
    email: EmailStr


class UserOut(Out):
    email: EmailStr
    theme: str
    is_admin: bool | None = None
    last_login: datetime | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    current_password: str | None = None
    email: EmailStr | None = None
    theme: str | None = None
    password: str | None = None
    is_admin: bool | None = None
    last_login: datetime | None = None


# -------------------------------------------------------- TOKEN -------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


# ------------------------------------------------------- KEYWORD ------------------------------------------------------


class KeywordCreate(BaseModel):
    name: str


class KeywordOut(KeywordCreate, OwnedOut):
    jobs: list["JobOut"] = (
        []
    )  # should return the min job data (including including application, updates and interviews)


class KeywordMinOut(KeywordCreate, OwnedOut):
    pass


class KeywordUpdate(KeywordCreate):
    name: str | None = None


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class AggregatorCreate(BaseModel):
    name: str
    url: str | None = None


class AggregatorOut(AggregatorCreate, OwnedOut):
    jobs: list["JobOut"] = []
    job_applications: list["JobApplicationOut"] = (
        []
    )  # should return the min job application data (including updates and interviews)


class AggregatorMinOut(AggregatorCreate, OwnedOut):
    pass


class AggregatorUpdate(AggregatorCreate):
    name: str | None = None


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class CompanyOut(CompanyCreate, OwnedOut):
    jobs: list["JobOut"] = []
    persons: list["PersonMinOut"] = []


class CompanyMinOut(CompanyCreate, OwnedOut):
    pass


class CompanyUpdate(CompanyCreate):
    name: str | None = None


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class LocationCreate(BaseModel):
    postcode: str | None = None
    city: str | None = None
    country: str | None = None


class LocationOut(LocationCreate, OwnedOut):
    name: str | None = None
    jobs: list["JobMinOut"] = []
    interviews: list["InterviewMinOut"] = []


class LocationMinOut(LocationCreate, OwnedOut):
    name: str | None = None


class LocationUpdate(LocationCreate):
    pass


# -------------------------------------------------------- FILES -------------------------------------------------------


class FileCreate(BaseModel):
    filename: str
    type: str
    content: str
    size: int


class FileOut(FileCreate, OwnedOut):
    pass


class FileUpdate(FileCreate):
    filename: str | None = None
    type: str | None = None
    content: str | None = None
    size: int | None = None


# ------------------------------------------------------- PERSON -------------------------------------------------------


class PersonCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    role: str | None = None

    # Foreign keys
    company_id: int | None = None


class PersonOut(PersonCreate, OwnedOut):
    company: CompanyMinOut | None = None
    interviews: list["InterviewMinOut"] = []
    jobs: list["JobMinOut"] = []
    name: str | None = None
    name_company: str | None = None


class PersonMinOut(PersonCreate, OwnedOut):
    name: str | None = None
    name_company: str | None = None


class PersonUpdate(PersonCreate):
    first_name: str | None = None
    last_name: str | None = None


# --------------------------------------------------------- JOB --------------------------------------------------------


class JobCreate(BaseModel):
    title: str
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    personal_rating: int | None = None
    url: str | None = None
    deadline: datetime | None = None
    note: str | None = None
    attendance_type: str | None = None

    # Foreign keys
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None
    source_id: int | None = None
    keywords: list[int] = []
    contacts: list[int] = []


class JobOut(JobCreate, OwnedOut):
    company: CompanyMinOut | None = None
    location: LocationMinOut | None = None
    source: AggregatorMinOut | None = None
    keywords: list[KeywordMinOut] = []
    contacts: list[PersonMinOut] = []
    job_application: Optional["JobApplicationOut"] = None  # call the full entry
    name: str


class JobMinOut(OwnedOut):
    title: str
    description: str | None
    salary_min: float | None
    salary_max: float | None
    personal_rating: int | None
    url: str | None
    deadline: datetime | None
    note: str | None
    attendance_type: str | None
    name: str

    # Foreign keys
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None
    source_id: int | None = None


class JobToChaseOut(JobOut):
    last_update_type: str = ""
    days_since_last_update: int = 0


class JobUpdate(JobCreate):
    title: str | None = None


# --------------------------------------------------- JOB APPLICATION --------------------------------------------------


class JobApplicationCreate(BaseModel):
    date: datetime
    url: str | None = None
    status: str
    note: str | None = None
    applied_via: str | None = None

    # Foreign keys
    job_id: int
    aggregator_id: int | None = None


class JobApplicationOut(JobApplicationCreate, OwnedOut):
    # last_update_type: str
    # last_update_date: datetime
    # days_since_last_update: int | None = None
    job: JobMinOut | None = None
    aggregator: AggregatorMinOut | None = None
    interviews: list["InterviewAppOut"] = []  # get the full interviews
    updates: list["JobApplicationUpdateAppOut"] = []  # get the full updates

    @computed_field
    @property
    def last_update_date(self) -> datetime:
        """Computed property that returns the most recent activity date from application date, interviews, or updates"""

        dates = [self.date]

        # Add interview dates
        if self.interviews:
            dates.extend([interview.date for interview in self.interviews])

        # Add update dates
        if self.updates:
            dates.extend([update.date for update in self.updates])

        # Filter out None values and return the maximum date
        valid_dates = [d for d in dates if d is not None]
        return max(valid_dates) if valid_dates else self.created_at

    @computed_field
    @property
    def last_update_type(self) -> str:
        """Computed property that returns the type of the most recent activity"""

        most_recent_date = self.date
        most_recent_type = "Application"

        # Check interviews
        if self.interviews:
            latest_interview = max(self.interviews, key=lambda x: x.date, default=None)
            if latest_interview and latest_interview.date > most_recent_date:
                most_recent_date = latest_interview.date
                most_recent_type = f"Interview ({len(self.interviews)})"

        # Check updates
        if self.updates:
            latest_update = max(self.updates, key=lambda x: x.date, default=None)
            if latest_update and latest_update.date > most_recent_date:
                most_recent_type = f"Update ({len(self.updates)})"

        return most_recent_type

    @computed_field
    @property
    def days_since_last_update(self) -> int:
        """Calculate days since last update"""
        now = datetime.now(UTC)
        return (self.last_update_date - now).days


class JobApplicationUpdate(JobApplicationCreate):
    date: datetime | None = None
    job_id: int | None = None
    status: str | None = None


# ------------------------------------------------------ INTERVIEW -----------------------------------------------------


class InterviewCreate(BaseModel):
    date: datetime
    type: str
    location_id: int | None = None
    job_application_id: int
    note: str | None = None
    interviewers: list[int] | None = None
    attendance_type: str | None = None


class InterviewOut(InterviewCreate, OwnedOut):
    location: LocationMinOut | None = None
    interviewers: list["PersonMinOut"] = []
    job_application: JobApplicationOut | None = None


class InterviewAppOut(InterviewCreate, OwnedOut):
    location: LocationMinOut | None = None
    interviewers: list["PersonMinOut"] = []


class InterviewMinOut(OwnedOut):
    date: datetime
    type: str
    location_id: int | None
    job_application_id: int
    note: str | None
    attendance_type: str | None


class InterviewUpdate(InterviewCreate):
    date: datetime | None = None
    job_application_id: int | None = None


# ----------------------------------------------- JOB APPLICATION UPDATE -----------------------------------------------


class JobApplicationUpdateCreate(BaseModel):
    date: datetime
    type: str
    job_application_id: int
    note: str | None = None


class JobApplicationUpdateOut(JobApplicationUpdateCreate, OwnedOut):
    job_application: JobApplicationOut | None = None


class JobApplicationUpdateAppOut(JobApplicationUpdateCreate, OwnedOut):
    pass


class JobApplicationUpdateUpdate(JobApplicationUpdateCreate):
    date: datetime | None = None
    type: str | None = None
    job_application_id: int | None = None
