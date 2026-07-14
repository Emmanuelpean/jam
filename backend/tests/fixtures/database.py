"""Database fixtures for test setup and session management."""

from typing import Any, Generator

import pytest
from sqlalchemy import create_engine, orm, text, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.database import Base, create_db_url
from tests.utils.seed_database import reset_database


def truncate_all_tables(engine: Engine) -> None:
    """Fast per-test reset: wipe all rows and reset identity sequences in a single statement."""

    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    if not table_names:
        return
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def worker_database_name(worker_id: str) -> str:
    """Generate unique database name for each worker."""

    database_name = "jam_test"
    if worker_id == "master":
        return database_name
    else:
        return f"{database_name}_{worker_id}"


@pytest.fixture(scope="session")
def database_url(worker_database_name: str) -> str:
    """Generate database URL for the worker."""

    return create_db_url(worker_database_name)


@pytest.fixture(scope="session")
def engine(database_url: str, worker_id: str) -> Generator[Engine, Any, None]:
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


@pytest.fixture
def session(engine: Engine) -> Generator[orm.Session, Any, None]:
    """Per-test session bound to a single connection inside an outer transaction that is rolled back
    on teardown, so tests never touch committed state. ``join_transaction_mode="create_savepoint"``
    makes every ``session.commit()`` (including those inside API endpoints under test) release and
    reopen a SAVEPOINT rather than committing the outer transaction, keeping tests isolated.

    Note: the whole test runs in one transaction, so PostgreSQL ``now()`` (``created_at``/``modified_at``
    defaults) is frozen for its duration. Rows created in the same test share a timestamp - order such
    queries by a tiebreaker (e.g. ``id``) rather than relying on ``created_at`` alone."""

    connection = engine.connect()
    transaction = connection.begin()

    session = sessionmaker(
        bind=connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )
    db = session()
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()
