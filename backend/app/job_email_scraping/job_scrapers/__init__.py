"""Job scraper module"""

import datetime as dt

from pydantic import BaseModel, Field


class Salary(BaseModel):
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None


class JobInfo(BaseModel):
    title: str | None = None
    description: str | None = None
    url: str | None = None
    raw_url: str | None = None
    deadline: dt.datetime | None = None
    salary: Salary = Field(default_factory=Salary)


class JobResult(BaseModel):
    platform: str | None = None
    job_id: str | None = None
    company: str | None = None
    company_id: str | None = None
    location: str | None = None
    raw: str | None = None
    job: JobInfo
