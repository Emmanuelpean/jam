"""Database fixtures for test setup and session management."""

from typing import Any, Generator
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, orm, Engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.database import create_db_url
from tests.utils.seed_database import reset_database
from tests.utils.test_data.geolocation import mock_geocoding_side_effect


@pytest.fixture(autouse=True)
def mock_geocoding_for_all_tests() -> Generator[None, Any, None]:
    """Mock geocoding API calls for all tests automatically"""
    with patch("app.geolocation.call_geocoding_api", side_effect=mock_geocoding_side_effect):
        yield


@pytest.fixture(scope="session")
def worker_database_name(worker_id) -> str:
    """Generate unique database name for each worker."""
    DATABASE_NAME = "jam_test"
    if worker_id == "master":
        return DATABASE_NAME
    else:
        return f"{DATABASE_NAME}_{worker_id}"


def create_db_engine(database_name: str, worker_id: str) -> Generator[Engine, Any, None]:
    """Create engine for a given database name.
    :param database_name: Name of the database to create.
    :param worker_id: ID of the worker process.
    :return: Engine instance."""

    database_url = create_db_url(database_name)
    is_parallel = worker_id != "master"

    if is_parallel:
        if database_exists(database_url):
            drop_database(database_url)
        create_database(database_url)
    else:
        if not database_exists(database_url):
            create_database(database_url)

    engine = create_engine(database_url)

    yield engine

    engine.dispose()

    if is_parallel:
        drop_database(database_url)


@pytest.fixture(scope="session")
def engine(worker_database_name, worker_id) -> Generator[Engine, Any, None]:
    """Create engine once per worker session, creating database first."""

    yield from create_db_engine(worker_database_name, worker_id)


def create_db_session(db_engine: Engine) -> Generator[orm.Session, Any, None]:
    """Reset the database and yield a fresh session.
    :param db_engine: Engine to create the session from.
    :return: Database session."""

    reset_database(db_engine, False)
    SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def session(engine) -> Generator[orm.Session, Any, None]:
    """Fixture that sets up and tears down a new database session for each test function."""

    yield from create_db_session(engine)
