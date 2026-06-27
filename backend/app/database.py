"""Database connection functions"""

import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# Context variable to track demo mode per-request
demo_mode = ContextVar("demo_mode", default=False)


def create_db_url(db_name: str = "") -> str:
    """Create a database URL from the database settings."""

    if not db_name:
        db_name = settings.database_name
    return (
        f"postgresql://{settings.database_username}:{settings.database_password}@"
        f"{settings.database_hostname}:{settings.database_port}/{db_name}"
    )


SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", create_db_url())
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Demo engine with search_path set to demo schema
demo_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c search_path=demo"})
demo_session_local = sessionmaker(autocommit=False, autoflush=False, bind=demo_engine)


def get_demo_db() -> Generator[Session, Any, None]:
    """Get a demo schema database session.
    :return: the demo database session."""

    db = demo_session_local()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, Any, None]:
    """Provide a database session scoped to a unit of work, closed on exit.

    Uses the demo schema when the ``demo_mode`` context var is set. Use this for background services
    and scripts (``with db_session() as db:``); request handlers use the ``get_db`` dependency.
    :return: the database session."""

    db = demo_session_local() if demo_mode.get(False) else session_local()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session, Any, None]:
    """Get the database session. Uses demo schema if demo_mode context var is set.
    :return: the database session."""

    with db_session() as db:
        yield db
