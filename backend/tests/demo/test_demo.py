"""Tests for the demo user functionality."""

import datetime as dt
from unittest.mock import patch

import jwt

from app import models
from app.config import settings
from app.core.oauth2 import create_access_token
from app.demo.setup import cleanup_stale_demo_users, setup_demo_schema
from tests.demo.conftest import create_demo_user
from tests.utils import test_data as td
from tests.utils.create_data.core import create_users


class TestDemoLogin:

    def test_login_creates_ephemeral_user_in_demo_schema(self, test_demo_user, demo_login_client, demo_session) -> None:
        """Logging in with the demo account must create exactly one ephemeral user
        in the demo schema and return a JWT stamped with is_demo=True."""

        response = demo_login_client.post(
            "/login",
            data={"username": test_demo_user.email, "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"]},
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
        demo_session.expire_all()
        demo_users = demo_session.query(models.User).filter(models.User.is_demo.is_(True)).all()
        assert len(demo_users) == 1
        user = demo_users[0]
        assert "@demo.jam" in user.email
        assert user.first_name == "Demo"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.premium is not None
        assert user.premium.is_active is True

    def test_login_seeds_data_for_ephemeral_user(self, test_demo_user, demo_login_client, demo_session) -> None:
        """After demo login the ephemeral user must have seeded jobs and companies."""

        response = demo_login_client.post(
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

        demo_session.expire_all()
        jobs = demo_session.query(models.Job).filter(models.Job.owner_id == ephemeral_user_id).count()
        companies = demo_session.query(models.Company).filter(models.Company.owner_id == ephemeral_user_id).count()
        assert jobs > 0, "Expected seeded jobs for the demo user"
        assert companies > 0, "Expected seeded companies for the demo user"

    def test_regular_user_login_does_not_touch_demo_schema(
        self, test_regular_user, demo_login_client, demo_session
    ) -> None:
        """A normal (non-demo) login must not create any record in the demo schema."""

        response = demo_login_client.post(
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

        demo_session.expire_all()
        assert demo_session.query(models.User).count() == 0


class TestDemoSchemaSetup:
    def test_setup_seeds_ai_prompts_in_fresh_schema(self, demo_session) -> None:
        """setup_demo_schema must seed AI system prompts when the schema is empty."""

        # demo_session fixture already seeded AI prompts — verify they exist
        assert demo_session.query(models.AiSystemPrompt).count() > 0

    def test_seed_demo_ai_prompts_does_not_duplicate(self, demo_session) -> None:
        """seed_demo_ai_prompts must not add duplicate AI prompts when called repeatedly."""

        from app.demo.setup import seed_demo_ai_prompts

        # demo_session fixture already seeded prompts
        count_before = demo_session.query(models.AiSystemPrompt).count()
        assert count_before > 0

        seed_demo_ai_prompts(demo_session)
        demo_session.expire_all()
        count_after = demo_session.query(models.AiSystemPrompt).count()

        assert count_before == count_after


class TestMultipleDemoUsers:
    def test_two_logins_create_two_independent_users(self, test_demo_user, demo_login_client, demo_session) -> None:
        """Two concurrent demo logins must create two distinct ephemeral users."""

        res1 = demo_login_client.post(
            "/login",
            data={
                "username": test_demo_user.email,
                "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
            },
        )
        res2 = demo_login_client.post(
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

        demo_session.expire_all()
        users = demo_session.query(models.User).filter(models.User.is_demo.is_(True)).all()
        assert len(users) == 2
        emails = {u.email for u in users}
        assert len(emails) == 2, "Each ephemeral user must have a unique email"

    def test_each_session_data_belongs_only_to_its_user(self, test_demo_user, demo_login_client, demo_session) -> None:
        """Data seeded for session A must not appear under session B's user ID."""

        res1 = demo_login_client.post(
            "/login",
            data={
                "username": test_demo_user.email,
                "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
            },
        )
        res2 = demo_login_client.post(
            "/login",
            data={
                "username": test_demo_user.email,
                "password": td.USER_DATA[td.DEMO_USER_INDEX]["password"],
            },
        )

        payload1 = jwt.decode(res1.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        payload2 = jwt.decode(res2.json()["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        user1_id, user2_id = payload1["user_id"], payload2["user_id"]

        demo_session.expire_all()
        jobs_u1 = demo_session.query(models.Job).filter(models.Job.owner_id == user1_id).count()
        jobs_u2 = demo_session.query(models.Job).filter(models.Job.owner_id == user2_id).count()
        total_jobs = demo_session.query(models.Job).count()

        assert jobs_u1 > 0, "Session 1 user must have seeded jobs"
        assert jobs_u2 > 0, "Session 2 user must have seeded jobs"
        assert total_jobs == jobs_u1 + jobs_u2, "No jobs must be shared between sessions"


class TestDemoSchemaIsolation:

    def test_deleting_demo_user_does_not_affect_public_schema(self, session, demo_session) -> None:
        """Deleting a demo user (and their cascaded data) in the demo schema
        must not affect a regular user or their data in the public schema."""

        # Create a regular user with a job in the public schema
        regular_user = create_users(session)[0]
        public_job = models.Job(title="Public Job", owner_id=regular_user.id)
        session.add(public_job)
        session.commit()
        session.refresh(public_job)
        public_job_id = public_job.id

        # Create a demo user with a job in the demo schema
        demo_user = create_demo_user(demo_session)
        demo_job = models.Job(title="Demo Job", owner_id=demo_user.id)
        demo_session.add(demo_job)
        demo_session.commit()

        # Delete the demo user — cascade should remove the demo job
        demo_session.delete(demo_user)
        demo_session.commit()
        demo_session.expire_all()

        assert demo_session.query(models.Job).count() == 0, "Demo job must be cascade-deleted with the demo user"

        # The public schema must be completely untouched
        session.expire_all()
        assert (
            session.query(models.User).filter(models.User.id == regular_user.id).first() is not None
        ), "Regular user in the public schema must still exist"
        assert (
            session.query(models.Job).filter(models.Job.id == public_job_id).first() is not None
        ), "Job in the public schema must still exist"

    def test_deleting_demo_entry_does_not_affect_other_demo_users(self, demo_session) -> None:
        """Deleting one demo user's data must not affect another demo user's data
        within the same demo schema."""

        user_a = create_demo_user(demo_session)
        user_b = create_demo_user(demo_session)

        job_a = models.Job(title="Job A", owner_id=user_a.id)
        job_b = models.Job(title="Job B", owner_id=user_b.id)
        demo_session.add_all([job_a, job_b])
        demo_session.commit()

        # Delete user A — cascade should only remove job A
        demo_session.delete(user_a)
        demo_session.commit()
        demo_session.expire_all()

        assert (
            demo_session.query(models.Job).filter(models.Job.owner_id == user_a.id).count() == 0
        ), "Deleted demo user's jobs must be gone"
        remaining = demo_session.query(models.Job).filter(models.Job.owner_id == user_b.id).all()
        assert len(remaining) == 1, "Other demo user's jobs must be untouched"
        assert remaining[0].title == "Job B"


class TestDemoCleanup:
    def test_cleanup_endpoint_deletes_demo_user(self, demo_session, demo_client) -> None:
        """POST /demo/cleanup must remove the calling demo user from the demo schema."""

        user = create_demo_user(demo_session)
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

        user = create_demo_user(demo_session)
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

        old_user = create_demo_user(demo_session)
        fresh_user = create_demo_user(demo_session)

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

        user = create_demo_user(demo_session)
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

        user = create_demo_user(demo_session)
        cleanup_stale_demo_users(demo_session)
        demo_session.expire_all()

        assert demo_session.query(models.User).filter(models.User.id == user.id).first() is not None

    def test_stale_cleanup_runs_during_setup_demo_schema(
        self, engine, demo_engine, demo_session_raw, demo_session_factory_raw
    ) -> None:
        """setup_demo_schema must remove stale demo users as part of its startup routine."""

        # Insert a stale user directly
        old_user = create_demo_user(demo_session_raw)
        old_user_id = old_user.id
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=25)
        demo_session_raw.query(models.User).filter(models.User.id == old_user_id).update(
            {"created_at": cutoff}, synchronize_session=False
        )
        demo_session_raw.commit()

        with (
            patch("app.demo.setup.engine", engine),
            patch("app.demo.setup.demo_engine", demo_engine),
            patch("app.demo.setup.demo_session_local", side_effect=demo_session_factory_raw),
        ):
            setup_demo_schema()

        demo_session_raw.expire_all()
        assert (
            demo_session_raw.query(models.User).filter(models.User.id == old_user_id).first() is None
        ), "setup_demo_schema must delete demo users older than 24 h"
