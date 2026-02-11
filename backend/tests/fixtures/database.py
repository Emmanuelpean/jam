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


@pytest.fixture(scope="session")
def database_url(worker_database_name) -> str:
    """Generate database URL for the worker."""

    return create_db_url(worker_database_name)


@pytest.fixture(scope="session")
def engine(database_url, worker_id) -> Generator[Engine, Any, None]:
    """Create engine once per worker session, creating database first."""
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


@pytest.fixture(scope="function")
def session(engine) -> Generator[orm.Session, Any, None]:
    """Fixture that sets up and tears down a new database session for each test function."""
    reset_database(engine, False)
    TestingSessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
