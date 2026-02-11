"""Fixtures for demo tests."""

import uuid

import pytest
from sqlalchemy import orm
from starlette.testclient import TestClient

from app import database, models
from app.job_rating.prompts import seed_ai_prompts
from app.main import app
from tests.fixtures.database import create_db_engine, create_db_session
from tests.utils.create_data.data_tables import create_geolocations


@pytest.fixture(scope="session")
def demo_engine(worker_database_name, worker_id):
    """Dedicated PostgreSQL database for demo tests.
    Created fresh for every pytest-xdist worker so parallel runs stay isolated."""

    yield from create_db_engine(f"{worker_database_name}_demo", worker_id)


@pytest.fixture
def demo_session_raw(demo_engine):
    """Clean session on the demo test DB with tables reset but NO seed data.
    Use this for tests that call setup_demo_schema (which seeds its own data)."""

    yield from create_db_session(demo_engine)


@pytest.fixture
def demo_session(demo_session_raw):
    """Clean session on the demo test DB, with all tables dropped and recreated.
    Seeds geolocations and AI prompts to mirror what setup_demo_schema does in production."""

    create_geolocations(demo_session_raw)
    seed_ai_prompts(demo_session_raw)
    return demo_session_raw


@pytest.fixture
def demo_session_factory_raw(demo_engine, demo_session_raw):
    """Session factory for the demo test DB without pre-seeded data.
    Use with demo_session_raw for tests that call setup_demo_schema."""

    return orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_engine)


@pytest.fixture
def demo_client(demo_session):
    """FastAPI test client whose get_db dependency returns the demo session."""

    def override_get_db():
        yield demo_session

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)


@pytest.fixture
def demo_login_client(session, demo_session):
    """FastAPI test client that overrides both get_db (public schema) and
    get_demo_db (demo schema) for login tests."""

    def override_get_db():
        yield session

    def override_get_demo_db():
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
        is_demo=True,
        is_active=True,
        is_verified=True,
        first_name="Demo",
        last_name="User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
