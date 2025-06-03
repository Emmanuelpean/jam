"""Schemas for the JAM database"""

from datetime import datetime

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


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------------------------------------- TOKEN -------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


# --------------------------------------------------------- JOB --------------------------------------------------------


class Job(BaseModel):
    title: str
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    personal_rating: int | None = None
    url: str | None = None
    company_id: int | None = None
    location_id: int | None = None
    duplicate_id: int | None = None


class JobOut(Job, Out):
    pass


class JobUpdate(Job):
    title: str | None = None


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class Location(BaseModel):
    postcode: str | None = None
    city: str | None = None
    country: str | None = None
    remote: bool | None = None


class LocationOut(Location, Out):
    pass


class LocationUpdate(Location):
    pass


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class Company(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class CompanyOut(Company, Out):
    pass


class CompanyUpdate(Company):
    name: str | None = None


# ------------------------------------------------------- PERSON -------------------------------------------------------


class Person(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    company_id: int


class PersonOut(Person, Out):
    pass


class PersonUpdate(Person):
    first_name: str | None = None
    last_name: str | None = None
    company_id: int | None = None


# ----------------------------------------------------- AGGREGATOR -----------------------------------------------------


class Aggregator(BaseModel):
    name: str
    url: str | None = None


class AggregatorOut(Aggregator, Out):
    pass


class AggregatorUpdate(Aggregator):
    name: str | None = None
