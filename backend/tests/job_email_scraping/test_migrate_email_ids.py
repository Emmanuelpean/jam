"""Tests for the external_email_id migration script (migrate_email_ids.py)."""

import datetime as dt
from contextlib import contextmanager
from typing import Callable
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from app import models
from app.emails.schemas import EmailData
from app.job_email_scraping import migrate_email_ids
from tests.fixtures.users import FixtureUser

BASE_DATE = dt.datetime(2025, 1, 1, 9, 0, 0, tzinfo=dt.timezone.utc)


@pytest.fixture
def make_email(test_regular_user: FixtureUser) -> Callable[..., models.JobEmail]:
    """Factory creating a JobEmail row with the given external_email_id/subject/date."""

    def _create(
        external_email_id: str,
        subject: str,
        date_received: dt.datetime,
    ) -> models.JobEmail:
        return test_regular_user.create_job_email(
            external_email_id=external_email_id,
            subject=subject,
            sender="alerts@example.com",
            date_received=date_received,
            platform="linkedin",
            body="<html>body</html>",
        )

    return _create


@pytest.fixture
def patch_dependencies(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> Callable[[list[EmailData]], mock.MagicMock]:
    """Patch get_db to yield the test session and EmailService to return the given vps emails."""

    @contextmanager
    def _fake_db_session():
        yield session

    def _patch(vps_emails: list[EmailData]) -> mock.MagicMock:
        monkeypatch.setattr(migrate_email_ids, "db_session", _fake_db_session)
        service = mock.MagicMock()
        service.get_emails.return_value = vps_emails
        monkeypatch.setattr(migrate_email_ids, "EmailService", lambda *a, **k: service)
        return service

    return _patch


def _vps_email(uid: str, subject: str, date: dt.datetime) -> EmailData:
    """Build a fake IMAP email entry as consumed by the migration script."""

    return EmailData(
        id=uid,
        message_id=f"<{uid}@example.com>",
        subject=subject,
        from_email="alerts@example.com",
        to_email="scraper@example.com",
        date=date,
        body="<html>body</html>",
    )


class TestRunMigration:
    """Test suite for the run_migration function."""

    MakeEmail = Callable[..., models.JobEmail]
    PatchDependencies = Callable[[list[EmailData]], mock.MagicMock]

    def test_dry_run_leaves_database_unchanged(
        self, make_email: MakeEmail, patch_dependencies: PatchDependencies
    ) -> None:
        email = make_email("100", "LinkedIn alert A", BASE_DATE)
        patch_dependencies([_vps_email("5", "LinkedIn alert A", BASE_DATE)])

        migrate_email_ids.run_migration(dry_run=True)

        assert email.external_email_id == "100"

    def test_apply_updates_external_email_id_to_uid(
        self, make_email: MakeEmail, patch_dependencies: PatchDependencies
    ) -> None:
        email = make_email("100", "LinkedIn alert A", BASE_DATE)
        patch_dependencies([_vps_email("5", "LinkedIn alert A", BASE_DATE)])

        migrate_email_ids.run_migration(dry_run=False)

        assert email.external_email_id == "5"

    def test_apply_updates_multiple_records(self, make_email: MakeEmail, patch_dependencies: PatchDependencies) -> None:
        date_b = BASE_DATE + dt.timedelta(days=1)
        email_a = make_email("100", "LinkedIn alert A", BASE_DATE)
        email_b = make_email("200", "LinkedIn alert B", date_b)
        patch_dependencies(
            [
                _vps_email("5", "LinkedIn alert A", BASE_DATE),
                _vps_email("7", "LinkedIn alert B", date_b),
            ]
        )

        migrate_email_ids.run_migration(dry_run=False)

        assert email_a.external_email_id == "5"
        assert email_b.external_email_id == "7"

    def test_jam_prefixed_records_are_ignored(
        self, make_email: MakeEmail, patch_dependencies: PatchDependencies
    ) -> None:
        jam_email = make_email("jam-abc", "Manual entry", BASE_DATE)
        seq_email = make_email("100", "LinkedIn alert A", BASE_DATE)
        # Only the numeric-id email has a matching vps entry; the jam-prefixed one is skipped entirely.
        patch_dependencies([_vps_email("5", "LinkedIn alert A", BASE_DATE)])

        migrate_email_ids.run_migration(dry_run=False)

        assert jam_email.external_email_id == "jam-abc"
        assert seq_email.external_email_id == "5"

    def test_raises_when_no_match_found(self, make_email: MakeEmail, patch_dependencies: PatchDependencies) -> None:
        make_email("100", "LinkedIn alert A", BASE_DATE)
        patch_dependencies([_vps_email("5", "Different subject", BASE_DATE)])

        with pytest.raises(AssertionError, match="Should be 1, Is 0"):
            migrate_email_ids.run_migration(dry_run=False)

    def test_raises_when_multiple_matches_found(
        self, make_email: MakeEmail, patch_dependencies: PatchDependencies
    ) -> None:
        make_email("100", "LinkedIn alert A", BASE_DATE)
        patch_dependencies(
            [
                _vps_email("5", "LinkedIn alert A", BASE_DATE),
                _vps_email("6", "LinkedIn alert A", BASE_DATE),
            ]
        )

        with pytest.raises(AssertionError, match="Should be 1, Is 2"):
            migrate_email_ids.run_migration(dry_run=False)

    def test_match_requires_both_subject_and_date(
        self, make_email: MakeEmail, patch_dependencies: PatchDependencies
    ) -> None:
        # Same subject but a different date must not match.
        make_email("100", "LinkedIn alert A", BASE_DATE)
        patch_dependencies([_vps_email("5", "LinkedIn alert A", BASE_DATE + dt.timedelta(days=2))])

        with pytest.raises(AssertionError, match="Should be 1, Is 0"):
            migrate_email_ids.run_migration(dry_run=False)
