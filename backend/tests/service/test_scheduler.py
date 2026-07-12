"""Unit tests for the database-driven service scheduler."""

import datetime as dt
from collections.abc import Callable
from contextlib import nullcontext
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.models import Service
from app.service.scheduler import ServiceScheduler, compute_next_run
from tests.base_test import BaseTest


def _utc(*args: int) -> dt.datetime:
    return dt.datetime(*args, tzinfo=dt.timezone.utc)


# ------------------------------------------------ COMPUTE NEXT RUN ------------------------------------------------


class TestComputeNextRun:
    def test_advances_one_period_when_just_due(self) -> None:
        """A slot that just fired advances by exactly one period."""

        base = _utc(2026, 1, 1, 12, 0, 0)
        now = _utc(2026, 1, 1, 12, 0, 1)
        assert compute_next_run(base, now, 3.0) == _utc(2026, 1, 1, 15, 0, 0)

    def test_keeps_phase_when_run_overruns(self) -> None:
        """If the run took a while, the next slot is still phase-aligned to base."""

        base = _utc(2026, 1, 1, 12, 0, 0)
        now = _utc(2026, 1, 1, 12, 20, 0)  # 20-minute run, period 3h
        assert compute_next_run(base, now, 3.0) == _utc(2026, 1, 1, 15, 0, 0)

    def test_skips_missed_slots_after_downtime(self) -> None:
        """After long downtime, jump to the next future slot rather than replaying each."""

        base = _utc(2026, 1, 1, 12, 0, 0)
        now = _utc(2026, 1, 1, 22, 30, 0)  # missed 15:00, 18:00, 21:00
        # Next future 3h slot phase-aligned to 12:00 is 00:00 next day.
        assert compute_next_run(base, now, 3.0) == _utc(2026, 1, 2, 0, 0, 0)

    def test_result_is_strictly_future(self) -> None:
        """The returned slot is always strictly greater than now."""

        base = _utc(2026, 1, 1, 12, 0, 0)
        now = _utc(2026, 1, 1, 15, 0, 0)  # exactly on a slot boundary
        assert compute_next_run(base, now, 3.0) == _utc(2026, 1, 1, 18, 0, 0)

    def test_none_base_uses_now(self) -> None:
        """With no base, the next run is one period from now."""

        now = _utc(2026, 1, 1, 12, 0, 0)
        assert compute_next_run(None, now, 2.0) == _utc(2026, 1, 1, 14, 0, 0)


# --------------------------------------------------- FIXTURES ---------------------------------------------------


def _make_service(
    session: Session,
    name: str = "fake_service",
    enabled: bool = True,
    next_run_at: dt.datetime | None = None,
    period: float = 3.0,
    parameters: dict | None = None,
    is_running: bool = False,
) -> Service:
    """Create and persist a Service row."""

    return BaseTest.create_service(
        session,
        name=name,
        run_period_hours=period,
        parameters=parameters or {},
        is_enabled=enabled,
        is_running=is_running,
        next_run_at=next_run_at,
    )


class _SyncThread:
    """Stand-in for threading.Thread that runs the target synchronously on start()."""

    def __init__(self, target: Callable | None = None, args: tuple = (), **_kwargs) -> None:
        self._target = target
        self._args = args

    def start(self) -> None:
        """Run the target synchronously."""
        if self._target:
            self._target(*self._args)


# -------------------------------------------------- RUN SERVICE --------------------------------------------------


class TestRunService(BaseTest):
    def test_runs_callable_with_parameters_and_advances_schedule(self, session: Session) -> None:
        """The registered callable runs with the row's parameters; schedule advances and clears running."""

        calls = []
        self.register_service("fake_service", lambda **kw: calls.append(kw))
        base = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        service = _make_service(session, next_run_at=base, parameters={"timedelta_days": 3})

        service_id = service.id
        scheduler = ServiceScheduler()
        with patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)):
            scheduler._run_service(service_id)

        assert calls == [{"timedelta_days": 3}]
        updated = self.get_by_id(session, Service, service_id)
        assert updated.is_running is False
        assert updated.next_run_at > dt.datetime.now(dt.timezone.utc)

    def test_advances_schedule_even_when_callable_raises(self, session: Session) -> None:
        """A failing run still advances the schedule and clears the running flag (no stuck service)."""

        def boom(**_kw):
            """Raise a runtime error"""
            raise RuntimeError("kaboom")

        self.register_service("fake_service", boom)
        base = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        service = _make_service(session, next_run_at=base)

        service_id = service.id
        scheduler = ServiceScheduler()
        with patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)):
            scheduler._run_service(service_id)

        updated = self.get_by_id(session, Service, service_id)
        assert updated.is_running is False
        assert updated.next_run_at > dt.datetime.now(dt.timezone.utc)

    def test_missing_service_is_skipped(self, session: Session) -> None:
        """A service id that no longer exists is skipped without error."""

        scheduler = ServiceScheduler()
        with patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)):
            scheduler._run_service(99999)  # no such row — must not raise

    def test_row_deleted_during_run_is_handled(self, session: Session) -> None:
        """If the row is deleted mid-run, the finally block skips the schedule update without error."""

        base = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        service_id = _make_service(session, next_run_at=base).id

        def delete_row(**_kw):
            """Delete the row during the run."""
            session.query(Service).filter(Service.id == service_id).delete()
            session.commit()

        self.register_service("fake_service", delete_row)
        scheduler = ServiceScheduler()
        with patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)):
            scheduler._run_service(service_id)  # must not raise

        assert self.get_by_id(session, Service, service_id) is None


# ----------------------------------------------------- TICK -----------------------------------------------------


class TestTick(BaseTest):
    def test_dispatches_only_due_enabled_services(self, session: Session) -> None:
        """Only enabled services whose next_run_at is due are dispatched."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)
        due = _make_service(session, name="due_service", enabled=True, next_run_at=past)
        _make_service(session, name="not_due_service", enabled=True, next_run_at=future)
        _make_service(session, name="disabled_service", enabled=False, next_run_at=past)

        scheduler = ServiceScheduler()
        scheduler._run_service = MagicMock()
        with (
            patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)),
            patch("app.service.scheduler.threading.Thread", _SyncThread),
        ):
            scheduler._tick()

        scheduler._run_service.assert_called_once_with(due.id)

    def test_null_next_run_at_is_due(self, session: Session) -> None:
        """An enabled service with no scheduled time is treated as due."""

        service = _make_service(session, name="never_run", enabled=True, next_run_at=None)

        scheduler = ServiceScheduler()
        scheduler._run_service = MagicMock()
        with (
            patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)),
            patch("app.service.scheduler.threading.Thread", _SyncThread),
        ):
            scheduler._tick()

        scheduler._run_service.assert_called_once_with(service.id)

    def test_skips_service_already_running(self, session: Session) -> None:
        """A service whose is_running flag is set is not dispatched again (overlap guard)."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        _make_service(session, name="busy_service", enabled=True, next_run_at=past, is_running=True)

        scheduler = ServiceScheduler()
        scheduler._run_service = MagicMock()
        with (
            patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)),
            patch("app.service.scheduler.threading.Thread", _SyncThread),
        ):
            scheduler._tick()

        scheduler._run_service.assert_not_called()

    def test_marks_service_running_before_dispatch(self, session: Session) -> None:
        """A dispatched service has its is_running flag committed before the worker runs."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)
        service = _make_service(session, name="due_service", enabled=True, next_run_at=past)

        scheduler = ServiceScheduler()
        scheduler._run_service = MagicMock()
        with (
            patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)),
            patch("app.service.scheduler.threading.Thread", _SyncThread),
        ):
            scheduler._tick()

        assert self.get_by_id(session, Service, service.id).is_running is True


# ----------------------------------------------------- START ----------------------------------------------------


class TestStart(BaseTest):
    def test_resets_stale_running_flags(self, session: Session) -> None:
        """Startup clears is_running flags stranded by a crash so those services can run again."""

        stuck_id = _make_service(session, name="stuck_service", enabled=True, is_running=True).id

        scheduler = ServiceScheduler()
        with (
            patch("app.service.scheduler.db_session", side_effect=lambda: nullcontext(session)),
            patch.object(ServiceScheduler, "_loop", lambda self: None),
        ):
            scheduler.start()
        scheduler.stop()

        assert self.get_by_id(session, Service, stuck_id).is_running is False
