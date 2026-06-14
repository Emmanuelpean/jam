"""Schemas for email data."""

from datetime import datetime

from pydantic import BaseModel


class EmailData(BaseModel):
    """Represents the content of a fetched email."""

    id: str
    message_id: str
    subject: str
    from_email: str
    to_email: str
    date: datetime
    body: str
