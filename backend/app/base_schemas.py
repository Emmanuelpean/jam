"""Pydantic schemas for input and output data validation and serialisation"""

import datetime as dt
from typing import Annotated

from pydantic import BaseModel, EmailStr, BeforeValidator

from app.utils import clean_email

EmailField = Annotated[EmailStr, BeforeValidator(clean_email)]


def serialise_relationships(value: list) -> list[int]:
    """Serialise relationships to list of IDs"""

    if not value:
        return []
    if isinstance(value[0], int):
        return value
    return [item.id for item in value]


class Out(BaseModel):
    """Base model for all output schemas"""

    id: int
    created_at: dt.datetime
    modified_at: dt.datetime


class OwnedOut(Out):
    """Base model for all output schemas owned by a user"""

    owner_id: int


class GenericResponse(BaseModel):
    success: bool
    message: str
    error_code: int | None = None
