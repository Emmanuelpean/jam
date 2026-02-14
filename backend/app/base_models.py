"""This module defines the database table models for the application using SQLAlchemy ORM. Each class represents a table in
the database, with its fields defining the table's columns and relationships. The module utilizes a `CommonBase` class
to provide a shared structure for all models, including common attributes like `id`, `created_at`, and `created_by`."""

import re

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, text, func
from sqlalchemy.ext.declarative import declared_attr


class CommonBase(object):
    """A base class that contains common attributes shared by all tables.
    The table name is automatically generated from the class name by converting CamelCase to snake_case.

    Attributes:
    -----------
    - `id` (int): Primary key of the record. Automatically populated upon creation.
    - `created_at` (datetime): The timestamp of when the record was created. Automatically populated upon creation.
    - `modified_at` (datetime): The timestamp of when the record was modified. Automatically updated upon updates."""

    # noinspection PyMethodParameters
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

    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
