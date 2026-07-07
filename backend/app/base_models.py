"""This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

import re
from enum import StrEnum

from sqlalchemy import Boolean, Column, Integer, ForeignKey, TIMESTAMP, text, func
from sqlalchemy.ext.declarative import declared_attr


class ProcessingStatus(StrEnum):
    """Outcome of a processing pipeline (job scraping, job rating).

    Stored as a VARCHAR (the enum value). ``PENDING`` covers "not yet finalised", including items
    that failed transiently and are scheduled for retry; only exhausted retries reach ``FAILED``.
    ``FILTERED`` is scraping-specific (the job matched an exclusion rule); job ratings never use it."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    COPIED = "copied"
    FILTERED = "filtered"


class CommonBase(object):
    """A base class that contains common attributes shared by all tables.
    The table name is automatically generated from the class name by converting CamelCase to snake_case.

    Attributes:
    -----------
    - `id` (int): Primary key of the record. Automatically populated upon creation.
    - `created_at` (datetime): The timestamp of when the record was created. Automatically populated upon creation.
    - `modified_at` (datetime): The timestamp of when the record was modified. Automatically updated upon updates."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Return the class name as table name e.g. JobApplication -> job_application"""

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    modified_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Owned(CommonBase):
    """A base class that contains common attributes shared by tables which entries have an owner.

    Attributes:
    -----------
    - `owner_id` (int): Foreign key linking the record to the user table."""

    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    is_tour = Column(Boolean, nullable=False, server_default=text("false"))
