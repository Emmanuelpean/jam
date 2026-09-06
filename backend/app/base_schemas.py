"""Pydantic schemas for input and output data validation and serialisation"""

import datetime as dt
from typing import Annotated

from pydantic import BaseModel, EmailStr, BeforeValidator, Field

from app.utilities.strings import clean_email

# --------------------------------------------------- COLUMN LIMITS ----------------------------------------------------


class ColumnLimits(BaseModel):
    # User / auth
    email: int = 254  # RFC 5321 maximum email address length
    password: int = 128
    first_name: int = 200
    last_name: int = 200
    # User preferences
    theme: int = 128
    theme_mode: int = 128
    app_version: int = 128
    token: int = 43  # secrets.token_urlsafe(32) always produces 43 chars
    tour_id: int = 128
    completed_tours: int = 20
    dashboard_layout: int = 100_000
    table_entity_type: int = 50
    table_entity_types: int = 500
    table_column_key: int = 100
    table_columns: int = 300
    table_sort_value: int = 500
    table_sort_entry_keys: int = 2
    # User profile
    experience: int = 10_000
    education: int = 3_500
    skills: int = 3_500
    qualities: int = 3_500
    interests: int = 3_500
    # Shared
    name: int = 400
    url: int = 2_048
    note: int = 10_000
    location: int = 1_000
    attendance_type: int = 100
    currency: int = 100
    description: int = 10_000
    # File
    file_name: int = 300
    file_mimetype: int = 100
    file_type: int = 100
    # Person
    phone: int = 30
    role: int = 200
    # Job
    job_title: int = 400
    application_status: int = 100
    applied_via: int = 100
    source_type: int = 100
    # Interview
    interview_type: int = 100
    # Update
    update_type: int = 100


COLUMN_LIMITS = ColumnLimits()

# ----------------------------------------------------------------------------------------------------------------------

EmailField = Annotated[EmailStr, BeforeValidator(clean_email), Field(max_length=COLUMN_LIMITS.email)]


def serialise_relationships(value: list) -> list[int]:
    """Serialise relationships to list of IDs"""

    if not value:
        return []
    if isinstance(value[0], int):
        return value
    return [item.id for item in value]


class OwnedCreate(BaseModel):
    """Base model for all create schemas"""

    is_tour: bool = False


class Out(BaseModel):
    """Base model for all output schemas"""

    id: int
    created_at: dt.datetime
    modified_at: dt.datetime


class OwnedOut(Out):
    """Base model for all output schemas owned by a user"""

    owner_id: int
    is_tour: bool = False


class GenericResponse(BaseModel):
    success: bool
    message: str
    error_code: int | None = None
