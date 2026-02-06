"""Database connection functions"""

import os
from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings


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


def get_db() -> Generator[Session, Any, None]:
    """Get the database session."""

    db = session_local()
    try:
        yield db
    finally:
        db.close()
