"""Database-driven scheduler that periodically runs due services."""

import datetime as dt
import math
import threading

from sqlalchemy import or_

from app.database import db_session
from app.service.models import Service
from app.service.registry import get_service_callable, sync_services_to_db
from app.utilities.logger import AppLogger

# Logger / log-file name for the scheduler itself.
SCHEDULER_LOG_NAME = "service_scheduler"


def compute_next_run(base: dt.datetime | None, now: dt.datetime, period_hours: float) -> dt.datetime:
    """Return the next scheduled run strictly after ``now``, phase-aligned to ``base``.

    Advances ``base`` in whole ``period_hours`` steps until the result is in the future, so missed
    slots (e.g. while the scheduler was down) are skipped rather than replayed.
    :param base: The slot that just fired (its ``next_run_at``); ``now`` is used if ``None``.
    :param now: Current time.
    :param period_hours: Interval between runs, in hours.
    :return: The next ``next_run_at``, strictly greater than ``now``."""

    period = dt.timedelta(hours=period_hours)
    if base is None:
        return now + period
    elapsed = (now - base).total_seconds()
    steps = math.floor(elapsed / period.total_seconds()) + 1
    return base + steps * period


class ServiceScheduler:
    """Polls the ``Service`` table and runs due services on worker threads."""

    def __init__(self, poll_interval_seconds: float = 30.0) -> None:
        """Initialise the scheduler.
        :param poll_interval_seconds: How often to poll the ``Service`` table for due runs."""

        self.poll_interval_seconds = poll_interval_seconds
        self.stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.logger = AppLogger.create_service_logger(SCHEDULER_LOG_NAME, "INFO")

    def start(self) -> None:
        """Start the scheduler poll loop in a daemon thread."""

        if self._thread is not None and self._thread.is_alive():
            self.logger.warning("Scheduler already running")
            return

        with db_session() as db:
            # Create rows for any newly-registered services (preserves existing rows / admin edits).
            created = sync_services_to_db(db)
            if created:
                self.logger.info(f"Seeded {created} new service(s) in the database")

            # Clear any is_running flags stranded by a crash so those services can run again. Safe
            # because only one scheduler process runs (SCHEDULER=true); see _tick for the overlap guard.
            stale = db.query(Service).filter(Service.is_running.is_(True)).update({Service.is_running: False})
            db.commit()
            if stale:
                self.logger.warning(f"Reset {stale} stale is_running flag(s) on startup")

        self.stop_event.clear()
        self._thread = threading.Thread(target=self._loop, name="service_scheduler", daemon=True)
        if self._thread:
            self._thread.start()
            self.logger.info(f"Service scheduler started (poll interval: {self.poll_interval_seconds}s)")

    def stop(self) -> None:
        """Signal the poll loop to stop."""

        self.logger.info("Stopping service scheduler")
        self.stop_event.set()

    def status(self) -> dict:
        """Return the scheduler's runtime status.

        Only meaningful on the process that runs the scheduler (``SCHEDULER=true``); elsewhere the
        loop never starts, so ``running`` is False.
        :return: ``{"running": bool, "poll_interval_seconds": float, "last_log": str | None}``."""

        return {
            "running": self._thread is not None and self._thread.is_alive(),
            "poll_interval_seconds": self.poll_interval_seconds,
            "last_log": self.logger.get_last_log_line(),
        }

    def _loop(self) -> None:
        """Poll for due services until stopped."""

        while not self.stop_event.is_set():
            try:
                self._tick()
            except Exception as exc:
                self.logger.exception(f"Error in scheduler tick: {exc}")
            self.stop_event.wait(timeout=self.poll_interval_seconds)

    def _tick(self) -> None:
        """Dispatch every enabled service that is due and not already running.

        ``is_running`` is the overlap guard: it is committed before the worker is dispatched, so the
        next tick filters the service out until its run finishes (and clears the flag). This is
        race-free because a single poll thread does all dispatching."""

        now = dt.datetime.now(dt.timezone.utc)
        with db_session() as db:
            due = (
                db.query(Service)
                .filter(Service.is_enabled.is_(True))
                .filter(Service.is_running.is_(False))
                .filter(or_(Service.next_run_at.is_(None), Service.next_run_at <= now))
                .all()
            )
            for service in due:
                service.is_running = True
                service.last_run_at = now
                db.commit()
                threading.Thread(
                    target=self._run_service,
                    args=(service.id,),
                    name=f"service_{service.name}",
                    daemon=True,
                ).start()

    def _run_service(self, service_id: int) -> None:
        """Run a single service and advance its schedule.
        :param service_id: Primary key of the ``Service`` row to run."""

        with db_session() as db:
            service = db.query(Service).filter(Service.id == service_id).first()
            if service is None:
                self.logger.warning(f"Service id {service_id} no longer exists; skipping run")
                return
            name = service.name
            parameters = service.parameters or {}
            try:
                fn = get_service_callable(name)
                self.logger.info(f"Running service '{name}' with parameters {parameters}")
                fn(**parameters)
                self.logger.info(f"Service '{name}' finished")
            except Exception as exc:
                self.logger.exception(f"Service '{name}' failed: {exc}")
            finally:
                # Re-fetch in case the row changed; advance the schedule and clear the running flag.
                # The row may have been deleted mid-run, in which case there is nothing to update.
                service = db.query(Service).filter(Service.id == service_id).first()
                if service is not None:
                    now = dt.datetime.now(dt.timezone.utc)
                    service.next_run_at = compute_next_run(service.next_run_at, now, service.run_period_hours)
                    service.is_running = False
                    db.commit()


service_scheduler = ServiceScheduler()
