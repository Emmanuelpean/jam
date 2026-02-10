"""Database connection functions"""

import os
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


def get_db() -> Generator[Session, Any, None]:
    """Get the database session. Uses demo schema if demo_mode context var is set.
    :return: the database session."""

    if demo_mode.get(False):
        db = demo_session_local()
    else:
        db = session_local()
    try:
        yield db
    finally:
        db.close()
