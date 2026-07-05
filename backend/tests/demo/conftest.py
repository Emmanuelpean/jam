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


@pytest.fixture(scope="session")
def demo_engine(engine):
    """Engine targeting a 'demo' schema inside the test database."""

    with engine.connect() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS demo CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA demo")
        conn.commit()

    demo_eng = create_engine(engine.url, connect_args={"options": "-c search_path=demo"})
    yield demo_eng
    demo_eng.dispose()


@pytest.fixture
def demo_session_raw(engine, demo_engine):
    """Clean demo schema session — drops and recreates the demo schema each test."""

    with engine.connect() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS demo CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA demo")
        conn.commit()
    Base.metadata.create_all(bind=demo_engine)

    session_factory = orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


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
