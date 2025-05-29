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
    description: str
    salary_min: int | None = None
    salary_max: int | None = None
    personal_rating: int | None = None
    url: str
    company_id: int
    location_id: int


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
