"""Database fixtures for test setup and session management."""

from typing import Any, Generator

import pytest
from sqlalchemy import create_engine, orm, text, Engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.database import Base, create_db_url
from tests.utils.seed_database import reset_database


def _truncate_all_tables(engine: Engine) -> None:
    """Fast per-test reset: wipe all rows and reset identity sequences in a single statement."""

    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    if not table_names:
        return
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def worker_database_name(worker_id) -> str:
    """Generate unique database name for each worker."""

    database_name = "jam_test"
    if worker_id == "master":
        return database_name
    else:
        return f"{database_name}_{worker_id}"


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

    reset_database(engine, False)

    yield engine

    engine.dispose()

    if is_parallel:
        drop_database(database_url)


@pytest.fixture(scope="function")
def session(engine: Engine) -> Generator[orm.Session, Any, None]:
    """Fixture that sets up and tears down a new database session for each test function."""
    _truncate_all_tables(engine)
    testing_session_local = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
