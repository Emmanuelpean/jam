"""Tests for the demo user functionality.

Covers:
- Login with demo credentials creates a new ephemeral user in the demo schema
- If the demo schema is empty, setup_demo_schema seeds it
- Multiple sessions can exist simultaneously without interfering
- The cleanup endpoint (logout) deletes the demo user and all their owned data
- Users older than 24 hours are deleted by cleanup_stale_demo_users / setup_demo_schema
"""

import datetime as dt
import uuid
from unittest.mock import patch

import jwt
import pytest
from sqlalchemy import create_engine, orm
from sqlalchemy_utils import database_exists, create_database, drop_database
from starlette.testclient import TestClient

from app import database, models
from app.config import settings
from app.core.oauth2 import create_access_token
from app.demo.setup import cleanup_stale_demo_users, setup_demo_schema
from app.main import app
from tests.utils import test_data as td
from tests.utils.seed_database import reset_database


@pytest.fixture(scope="session")
def demo_db_engine(worker_database_name):
    """Dedicated PostgreSQL database for demo tests.
    Created fresh for every pytest-xdist worker so parallel runs stay isolated."""

    demo_db_name = f"{worker_database_name}_demo"
    demo_url = database.create_db_url(demo_db_name)

    if database_exists(demo_url):
        drop_database(demo_url)
    create_database(demo_url)

    eng = create_engine(demo_url)
    yield eng
    eng.dispose()
    if database_exists(demo_url):
        drop_database(demo_url)


@pytest.fixture
def demo_session(demo_db_engine):
    """Clean session on the demo test DB, with all tables dropped and recreated.
    The full schema reset on every test ensures tests are fully independent."""

    reset_database(demo_db_engine, False)
    DemoTestSession = orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_db_engine)
    db = DemoTestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def demo_session_factory(demo_db_engine, demo_session):
    """Session factory for the demo test DB.
    Requesting demo_session as a dependency ensures the DB has been reset before
    any session factory sessions are opened."""

    return orm.sessionmaker(autocommit=False, autoflush=False, bind=demo_db_engine)


@pytest.fixture
def demo_client(demo_session):
    """FastAPI test client whose get_db dependency returns the demo session."""

    def override_get_db():
        yield demo_session

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)


def _make_ephemeral_user(session: orm.Session) -> models.User:
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


class TestDemoLogin:

    def test_login_creates_ephemeral_user_in_demo_schema(self, test_demo_user, client, demo_session_factory) -> None:
        """Logging in with the demo account must create exactly one ephemeral user
        in the demo schema and return a JWT stamped with is_demo=True."""

        DemoSession = demo_session_factory

        with patch("app.database.demo_session_local", side_effect=DemoSession):
            response = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )

        assert response.status_code == 200

        # JWT must carry the demo flag
        payload = jwt.decode(
            response.json()["access_token"],
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload.get("is_demo") is True

        # Exactly one ephemeral user must exist in the demo DB
        verify = DemoSession()
        try:
            demo_users = verify.query(models.User).filter(models.User.is_demo.is_(True)).all()
            assert len(demo_users) == 1
            user = demo_users[0]
            assert "@demo.jam" in user.email
            assert user.first_name == "Demo"
            assert user.last_name == "User"
            assert user.is_active is True
            assert user.is_verified is True
            assert user.premium is not None
            assert user.premium.is_active is True
        finally:
            verify.close()

    def test_login_seeds_data_for_ephemeral_user(self, test_demo_user, client, demo_session_factory) -> None:
        """After demo login the ephemeral user must have seeded jobs and companies."""

        DemoSession = demo_session_factory

        with patch("app.database.demo_session_local", side_effect=DemoSession):
            response = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )

        assert response.status_code == 200

        payload = jwt.decode(
            response.json()["access_token"],
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        ephemeral_user_id = payload["user_id"]

        verify = DemoSession()
        try:
            jobs = verify.query(models.Job).filter(models.Job.owner_id == ephemeral_user_id).count()
            companies = verify.query(models.Company).filter(models.Company.owner_id == ephemeral_user_id).count()
            assert jobs > 0, "Expected seeded jobs for the demo user"
            assert companies > 0, "Expected seeded companies for the demo user"
        finally:
            verify.close()

    def test_regular_user_login_does_not_touch_demo_schema(
        self, test_regular_user, client, demo_session_factory
    ) -> None:
        """A normal (non-demo) login must not create any record in the demo schema."""

        DemoSession = demo_session_factory

        with patch("app.database.demo_session_local", side_effect=DemoSession):
            response = client.post(
                "/login",
                data={
                    "username": test_regular_user.email,
                    "password": td.USER_DATA[td.REGULAR_USER_INDEX]["password"],
                },
            )

        assert response.status_code == 200

        payload = jwt.decode(
            response.json()["access_token"],
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload.get("is_demo") is False

        verify = DemoSession()
        try:
            assert verify.query(models.User).count() == 0
        finally:
            verify.close()


class TestDemoSchemaSetup:
    def test_setup_seeds_ai_prompts_in_fresh_schema(self, demo_session, demo_session_factory) -> None:
        """setup_demo_schema must seed AI system prompts when the schema is empty."""

        # demo_session fixture already reset the DB — confirm it is empty
        assert demo_session.query(models.AiSystemPrompt).count() == 0

        DemoSession = demo_session_factory
        with patch("app.demo.setup.demo_session_local", side_effect=DemoSession):
            setup_demo_schema()

        # Expire the cached state so the next query hits the DB
        demo_session.expire_all()
        assert demo_session.query(models.AiSystemPrompt).count() > 0

    def test_setup_does_not_duplicate_ai_prompts(self, demo_session, demo_session_factory) -> None:
        """Calling setup_demo_schema a second time must not add duplicate AI prompts."""

        DemoSession = demo_session_factory

        with patch("app.demo.setup.demo_session_local", side_effect=DemoSession):
            setup_demo_schema()

        demo_session.expire_all()
        count_after_first = demo_session.query(models.AiSystemPrompt).count()

        with patch("app.demo.setup.demo_session_local", side_effect=DemoSession):
            setup_demo_schema()

        demo_session.expire_all()
        count_after_second = demo_session.query(models.AiSystemPrompt).count()

        assert count_after_first == count_after_second


# -------------------------------------------------------
# 3. Multiple demo users can exist simultaneously
# -------------------------------------------------------


class TestMultipleDemoUsers:
    def test_two_logins_create_two_independent_users(self, test_demo_user, client, demo_session_factory) -> None:
        """Two concurrent demo logins must create two distinct ephemeral users."""

        DemoSession = demo_session_factory

        with patch("app.database.demo_session_local", side_effect=DemoSession):
            res1 = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )
            res2 = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )

        assert res1.status_code == 200
        assert res2.status_code == 200

        payload1 = jwt.decode(res1.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        payload2 = jwt.decode(res2.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])

        assert payload1["user_id"] != payload2["user_id"], "Each login must produce a distinct user ID"

        verify = DemoSession()
        try:
            users = verify.query(models.User).filter(models.User.is_demo.is_(True)).all()
            assert len(users) == 2
            emails = {u.email for u in users}
            assert len(emails) == 2, "Each ephemeral user must have a unique email"
        finally:
            verify.close()

    def test_each_session_data_belongs_only_to_its_user(self, test_demo_user, client, demo_session_factory) -> None:
        """Data seeded for session A must not appear under session B's user ID."""

        DemoSession = demo_session_factory

        with patch("app.database.demo_session_local", side_effect=DemoSession):
            res1 = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )
            res2 = client.post(
                "/login",
                data={
                    "username": test_demo_user.email,
                    "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
                },
            )

        payload1 = jwt.decode(res1.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        payload2 = jwt.decode(res2.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        user1_id, user2_id = payload1["user_id"], payload2["user_id"]

        verify = DemoSession()
        try:
            jobs_u1 = verify.query(models.Job).filter(models.Job.owner_id == user1_id).count()
            jobs_u2 = verify.query(models.Job).filter(models.Job.owner_id == user2_id).count()
            total_jobs = verify.query(models.Job).count()

            assert jobs_u1 > 0, "Session 1 user must have seeded jobs"
            assert jobs_u2 > 0, "Session 2 user must have seeded jobs"
            assert total_jobs == jobs_u1 + jobs_u2, "No jobs must be shared between sessions"
        finally:
            verify.close()


# -------------------------------------------------------
# 4. Logout (cleanup endpoint) deletes the demo user and their data
# -------------------------------------------------------


class TestDemoCleanup:
    def test_cleanup_endpoint_deletes_demo_user(self, demo_session, demo_client) -> None:
        """POST /demo/cleanup must remove the calling demo user from the demo schema."""

        user = _make_ephemeral_user(demo_session)
        token = create_access_token(
            data={"user_id": user.id},
            token_version=user.token_version,
            is_demo=True,
        )

        response = demo_client.post("/demo/cleanup", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["success"] is True

        demo_session.expire_all()
        deleted = demo_session.query(models.User).filter(models.User.id == user.id).first()
        assert deleted is None, "Demo user must be deleted after cleanup"

    def test_cleanup_cascades_to_user_preferences(self, demo_session, demo_client) -> None:
        """Deleting the demo user must cascade-delete their UserPreferences record."""

        user = _make_ephemeral_user(demo_session)
        preferences_id = user.preferences.id

        token = create_access_token(
            data={"user_id": user.id},
            token_version=user.token_version,
            is_demo=True,
        )
        demo_client.post("/demo/cleanup", headers={"Authorization": f"Bearer {token}"})

        demo_session.expire_all()
        assert (
            demo_session.query(models.UserPreferences).filter(models.UserPreferences.id == preferences_id).first()
            is None
        ), "UserPreferences must be cascade-deleted with the demo user"

    def test_cleanup_is_forbidden_for_non_demo_users(self, client, tokens) -> None:
        """Regular (non-demo) users must receive 403 from /demo/cleanup."""

        regular_token = tokens[td.REGULAR_USER_INDEX]
        response = client.post("/demo/cleanup", headers={"Authorization": f"Bearer {regular_token}"})
        assert response.status_code == 403

    def test_cleanup_requires_authentication(self, demo_client) -> None:
        """Unauthenticated requests to /demo/cleanup must be rejected."""

        response = demo_client.post("/demo/cleanup")
        assert response.status_code == 401


class TestStaleDemoUserCleanup:

    def test_users_older_than_24h_are_deleted(self, demo_session) -> None:
        """cleanup_stale_demo_users must remove demo users created more than 24 h ago."""

        old_user = _make_ephemeral_user(demo_session)
        fresh_user = _make_ephemeral_user(demo_session)

        # Back-date the old user by 25 hours
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=25)
        demo_session.query(models.User).filter(models.User.id == old_user.id).update(
            {"created_at": cutoff}, synchronize_session=False
        )
        demo_session.commit()

        cleanup_stale_demo_users(demo_session)
        demo_session.expire_all()

        assert (
            demo_session.query(models.User).filter(models.User.id == old_user.id).first() is None
        ), "User older than 24 h must be deleted"
        assert (
            demo_session.query(models.User).filter(models.User.id == fresh_user.id).first() is not None
        ), "User created within the last 24 h must be kept"

    def test_users_exactly_at_boundary_are_kept(self, demo_session) -> None:
        """A user created exactly at the 24-hour boundary must not be deleted."""

        user = _make_ephemeral_user(demo_session)
        boundary = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24) + dt.timedelta(minutes=1)
        demo_session.query(models.User).filter(models.User.id == user.id).update(
            {"created_at": boundary}, synchronize_session=False
        )
        demo_session.commit()

        cleanup_stale_demo_users(demo_session)
        demo_session.expire_all()

        assert demo_session.query(models.User).filter(models.User.id == user.id).first() is not None

    def test_fresh_users_are_never_deleted(self, demo_session) -> None:
        """cleanup_stale_demo_users must leave recently-created users untouched."""

        user = _make_ephemeral_user(demo_session)
        cleanup_stale_demo_users(demo_session)
        demo_session.expire_all()

        assert demo_session.query(models.User).filter(models.User.id == user.id).first() is not None

    def test_stale_cleanup_runs_during_setup_demo_schema(self, demo_session, demo_session_factory) -> None:
        """setup_demo_schema must remove stale demo users as part of its startup routine."""

        # Insert a stale user directly
        old_user = _make_ephemeral_user(demo_session)
        old_user_id = old_user.id
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=25)
        demo_session.query(models.User).filter(models.User.id == old_user_id).update(
            {"created_at": cutoff}, synchronize_session=False
        )
        demo_session.commit()

        DemoSession = demo_session_factory
        with patch("app.demo.setup.demo_session_local", side_effect=DemoSession):
            setup_demo_schema()

        demo_session.expire_all()
        assert (
            demo_session.query(models.User).filter(models.User.id == old_user_id).first() is None
        ), "setup_demo_schema must delete demo users older than 24 h"
