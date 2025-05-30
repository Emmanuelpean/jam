from datetime import datetime

from pydantic import BaseModel, EmailStr


# -------------------------------------------------------- USER --------------------------------------------------------


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    id: int
    username: str
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


class JobOut(BaseModel):
    title: str
    description: str
    salary_min: int
    salary_max: int
    personal_rating: int
    url: str
    company_id: int
    location_id: int


class JobCreate(BaseModel):
    title: str
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    personal_rating: int | None = None
    url: str | None = None
    company_id: int | None = None
    location_id: int | None = None


# ------------------------------------------------------ LOCATION ------------------------------------------------------


class Location(BaseModel):
    postcode: str | None = None
    city: str | None = None
    country: str | None = None
    remote: bool | None = None


class LocationOut(Location):
    id: int
    created_at: datetime
    owner_id: int


# ------------------------------------------------------- COMPANY ------------------------------------------------------


class Company(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class CompanyOut(Company):
    id: int
    created_at: datetime
    owner_id: int


class CompanyUpdate(Company):
    name: str | None = None


# ------------------------------------------------------- PERSON -------------------------------------------------------


class Person(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    company_id: int


class PersonOut(Person):
    id: int
    created_at: datetime
    owner_id: int


class PersonUpdate(Person):
    first_name: str | None = None
    last_name: str | None = None
    company_id: int | None = None
