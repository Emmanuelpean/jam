"""Fixtures for demo tests."""

import uuid

import pytest
from sqlalchemy import create_engine, orm
from starlette.testclient import TestClient

from app import database, models
from app.database import Base
from app.job_rating.prompts import seed_ai_prompts
from app.main import app
from tests.utils.create_data.data_tables import create_geolocations


def _recreate_demo_schema(engine) -> None:
    """Drop and recreate an empty 'demo' schema in the test database."""

    with engine.connect() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS demo CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA demo")
        conn.commit()


@pytest.fixture(scope="session")
def demo_engine(engine):
    """Engine targeting a 'demo' schema inside the test database, created once with all tables.
    Per-test isolation is handled by transaction rollback in ``demo_session_raw`` rather than by
    recreating the schema, so the expensive DDL runs a single time per worker session."""

    _recreate_demo_schema(engine)
    demo_eng = create_engine(engine.url, connect_args={"options": "-c search_path=demo"})
    Base.metadata.create_all(bind=demo_eng)
    yield demo_eng
    demo_eng.dispose()


@pytest.fixture
def demo_session_raw(demo_engine):
    """Per-test demo schema session bound to a single connection inside an outer transaction that is
    rolled back on teardown - the demo-schema counterpart of the public ``session`` fixture. See its
    docstring for the ``join_transaction_mode`` savepoint mechanics and the frozen-``now()`` caveat."""

    connection = demo_engine.connect()
    transaction = connection.begin()

    session = orm.sessionmaker(
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


@pytest.fixture
def demo_session(demo_session_raw):
    """Demo session pre-seeded with geolocations and AI prompts, mirroring setup_demo_schema in production.
    Seeds are rolled back with the rest of the test's transaction."""

    create_geolocations(demo_session_raw)
    seed_ai_prompts(demo_session_raw)
    return demo_session_raw


@pytest.fixture
def demo_session_untracked(engine, demo_engine):
    """Non-transactional demo session that commits for real, for tests that exercise the DDL lifecycle
    (setup_demo_schema drops/recreates the schema and so cannot run inside the rollback fixture).
    The schema is recreated on entry and on exit: these tests commit for real, and the rows they
    leave behind would collide with the seeding done by the transactional fixtures."""

    _recreate_demo_schema(engine)
    Base.metadata.create_all(bind=demo_engine)
    session_factory = orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        _recreate_demo_schema(engine)
        Base.metadata.create_all(bind=demo_engine)


@pytest.fixture
def demo_session_factory_raw(demo_engine):
    """Session factory for the demo test DB without pre-seeded data.
    Use with demo_session_untracked for tests that call setup_demo_schema."""

    return orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_engine)


@pytest.fixture
def demo_client(demo_session):
    """FastAPI test client whose get_db dependency returns the demo session."""

    def override_get_db():
        """Return the demo session for demo routes."""
        yield demo_session

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)


@pytest.fixture
def demo_login_client(session, demo_session):
    """FastAPI test client that overrides both get_db (public schema) and
    get_demo_db (demo schema) for login tests."""

    def override_get_db():
        """Return the public session for public routes."""
        yield session

    def override_get_demo_db():
        """Return the demo session for demo routes."""
        yield demo_session

    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[database.get_demo_db] = override_get_demo_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)
    app.dependency_overrides.pop(database.get_demo_db, None)


def create_demo_user(session: orm.Session) -> models.User:
    """Insert a minimal demo ephemeral user and return the committed instance."""

    user = models.User(
        email=f"demo-{uuid.uuid4().hex[:12]}@demo.jam",
        password="hashed_password",
        is_active=True,
        is_verified=True,
        first_name="Demo",
        last_name="User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
