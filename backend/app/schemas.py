"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

from datetime import datetime, UTC

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
    is_admin: bool = False
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
    """Keyword create schema"""

    name: str


class KeywordOut(KeywordCreate, OwnedOut):
    """Keyword output schema with full job data"""

    jobs: list["JobOut"] = []


class KeywordMinOut(KeywordCreate, OwnedOut):
    """Bare Keyword output schema"""

    pass


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

    jobs: list["JobOut"] = []
    job_applications: list["JobOut"] = []


class AggregatorMinOut(AggregatorCreate, OwnedOut):
    """Bare aggregator output schema"""

    pass


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

    jobs: list["JobOut"] = []
    persons: list["PersonMinOut"] = []


class CompanyMinOut(CompanyCreate, OwnedOut):
    """Bare company output schema"""

    pass


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
    jobs: list["JobOut"] = []
    interviews: list["InterviewMinOut"] = []


class LocationMinOut(LocationCreate, OwnedOut):
    """Bare location output schema"""

    name: str | None = None


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

    company: CompanyMinOut | None = None
    interviews: list["InterviewMinOut"] = []
    jobs: list["JobOut"] = []
    name: str | None = None
    name_company: str | None = None


class PersonMinOut(PersonCreate, OwnedOut):
    """Bare person output schema"""

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
    application_date: datetime
    application_url: str | None = None
    application_status: str
    application_note: str | None = None
    applied_via: str | None = None

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
    """Job output schema with bare company, location, aggregator, keywords, contacts data and semi-full interview and update data"""

    company: CompanyMinOut | None = None
    location: LocationMinOut | None = None
    source: AggregatorMinOut | None = None
    keywords: list[KeywordMinOut] = []
    contacts: list[PersonMinOut] = []
    application_aggregator: AggregatorMinOut | None = None
    interviews: list["InterviewAppOut"] = []  # get the full interviews
    updates: list["JobApplicationUpdateAppOut"] = []  # get the full updates
    name: str

    @computed_field
    @property
    def last_update_date(self) -> datetime:
        """Computed property that returns the most recent activity date from application date, interviews, or updates"""

        if self.application_date is None:
            return None

        dates = [self.application_date]

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

        if self.application_date is None:
            return None

        most_recent_date = self.application_date
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
        """Calculate days since the last update"""

        now = datetime.now(UTC)
        return (self.last_update_date - now).days


class JobMinOut(OwnedOut):
    """Bare job output schema"""

    title: str
    description: str | None
    salary_min: float | None
    salary_max: float | None
    personal_rating: int | None
    url: str | None
    deadline: datetime | None
    note: str | None
    attendance_type: str | None
    application_date: datetime
    application_url: str | None = None
    application_status: str
    application_note: str | None = None
    applied_via: str | None = None
    name: str

    # Foreign keys
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None
    source_id: int | None = None
    application_aggregator_id: int | None = None


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

    location: LocationMinOut | None = None
    interviewers: list[PersonMinOut] = []
    job: JobOut | None = None


class InterviewAppOut(InterviewCreate, OwnedOut):
    """Interview output with bare location and person data"""

    location: LocationMinOut | None = None
    interviewers: list[PersonMinOut] = []


class InterviewMinOut(OwnedOut):
    """Bare interview output schema"""

    date: datetime
    type: str
    location_id: int | None
    job_id: int
    note: str | None
    attendance_type: str | None


class InterviewUpdate(InterviewCreate):
    """Interview update schema"""

    date: datetime | None = None
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

    job: JobOut | None = None


class JobApplicationUpdateAppOut(JobApplicationUpdateCreate, OwnedOut):
    """Job Application Update output"""

    pass


class JobApplicationUpdateUpdate(JobApplicationUpdateCreate):
    """Job Application Update update schema"""

    date: datetime | None = None
    type: str | None = None
    job_id: int | None = None
