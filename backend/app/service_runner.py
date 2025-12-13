"""Module to run a generic service periodically in a separate thread."""

import datetime as dt
import os
import threading
import time

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.config import settings
from app.routers import assert_admin
from app.utils import AppLogger


class ServiceRunner:
    """Class to run a generic service periodically in a separate thread.
    :ivar service_name: name of the service to run
    :ivar service_kwargs: keyword arguments passed to the service_function
    :ivar service_function: function to run periodically"""

    service_name = ""
    service_kwargs = dict()
    service_function = None
    period_hours = 3.0

    def __init__(self) -> None:
        """Initialise the service runner instance."""

        self.service_runner_name = self.service_name + "_runner"
        self.service_runner_thread = None
        self.stop_event = threading.Event()
        self.service_runner_thread_status = "stopped"
        self.service_running = False
        self.sleep_until = None
        self.sleep_start = None
        self.logger = AppLogger.create_service_logger(self.service_runner_name, "INFO")
        self.logger.info(self.service_runner_name + " initialised")

    def start_runner(self, period_hours: float = 3.0, **kwargs) -> None:
        """Start the service runner
        :param period_hours: Maximum hours between each service run
        :param kwargs: keyword arguments passed to the service_function"""

        if self.service_runner_thread_status in ("started", "starting", "stopping"):
            self.logger.warning(f"Cannot start service runner - current status: {self.service_runner_thread_status}")
            return

        self.logger.info(f"Starting service runner (period: {period_hours}h)")
        self.service_runner_thread_status = "starting"

        # Store parameters
        self.period_hours = period_hours
        for kwarg in kwargs:
            self.service_kwargs[kwarg] = kwargs[kwarg]

        # Clear the stop event
        self.stop_event.clear()

        # Start the service in a separate thread
        self.service_runner_thread = threading.Thread(
            target=self._run_service,
            args=(period_hours,),
        )
        self.service_runner_thread.daemon = True
        self.service_runner_thread.start()

    def stop_runner(self) -> None:
        """Stop the scraping service"""

        if self.service_runner_thread_status in ("stopped", "starting", "stopping"):
            self.logger.warning(f"Cannot stop service - current status: {self.service_runner_thread_status}")
            return

        self.logger.info("Stopping service")
        self.service_runner_thread_status = "stopping"
        self.stop_event.set()

    def _run_service(self, period_hours: float) -> None:
        """Internal method that runs the service
        :param period_hours: Hours between each scraping run"""

        try:
            self.service_runner_thread_status = "started"
            self.logger.info("Service runner thread started successfully")

            while not self.stop_event.is_set():
                try:
                    # Run the scraping
                    self.logger.info(f"Starting service ({self.service_kwargs})")
                    self.service_running = True
                    result = self.service_function(**self.service_kwargs)
                    self.service_running = False

                    self.logger.info(f"Service completed - duration: {result.run_duration:.2f}s")

                    duration = result.run_duration
                    sleep_time = max([0, period_hours * 3600 - duration])

                    # Track sleep timing
                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + sleep_time

                    self.logger.info(f"Sleeping for {sleep_time:.2f}s until next run")

                    if self.stop_event.wait(timeout=sleep_time):
                        self.logger.info("Stop event received during sleep")
                        break

                    # Clear sleep tracking after waking
                    self.sleep_start = None
                    self.sleep_until = None

                except Exception as e:
                    self.logger.exception(f"Error during service runner: {e}")
                    self.service_running = False

                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + 300

                    self.logger.info("Waiting 5 minutes before retry after error")

                    if self.stop_event.wait(timeout=300):  # 5 minutes
                        self.logger.info("Stop event received during error recovery")
                        break

                    self.sleep_start = None
                    self.sleep_until = None
        finally:
            self.logger.info("Service runner ended")
            self.service_runner_thread_status = "stopped"
            self.sleep_start = None
            self.sleep_until = None

    def status(self) -> dict:
        """Get the current status of the service"""

        return {
            "service_runner_status": self.service_runner_thread_status,
            "service_running": self.service_running,
            "service_kwargs": self.service_kwargs,
            "period_hours": self.period_hours,
            "sleep_until": self.sleep_until,
        }


def start_scraper(
    service_runner: ServiceRunner,
    current_user: models.User,
    period_hours: float | int,
    **kwargs,
) -> dict:
    """Start the service runner with the specified period.
    :param service_runner: ServiceRunner instance
    :param current_user: Current authenticated user
    :param period_hours: period between runs in hours
    :param kwargs: keyword arguments containing keyword arguments passed to the start_runner method of ServiceRunner"""

    assert_admin(current_user)
    try:
        service_runner.start_runner(period_hours=period_hours, **kwargs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start service runner: {str(e)}",
        )
    return {"detail": f"Service runner started (period_hours={period_hours})"}


def stop_scraper(
    service_runner: ServiceRunner,
    current_user: models.User,
) -> dict:
    """Stop the service runner.
    :param service_runner: ServiceRunner instance
    :param current_user: Current authenticated user"""

    assert_admin(current_user)
    try:
        service_runner.stop_runner()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop service runner: {str(e)}",
        )
    return {"detail": "Service runner stopped"}


def scraper_status(
    service_runner: ServiceRunner,
    current_user: models.User,
) -> dict:
    """Get the current status service runner.
    :param service_runner: ServiceRunner instance
    :param current_user: Current authenticated user"""

    assert_admin(current_user)
    return service_runner.status()


def get_service_logs(
    logger_name: str,
    lines: int,
    current_user: models.User,
) -> dict:
    """Get the last N lines from the service log file
    :param lines: Number of lines to retrieve (default 100, max 10000)
    :param logger_name: Name of the logger / log file
    :param current_user: Current authenticated user"""

    assert_admin(current_user)

    log_file_path = os.path.join(settings.log_directory, logger_name + ".log")

    if not os.path.exists(log_file_path):
        return {"lines": [], "total_lines": 0}

    try:
        with open(log_file_path, "r") as f:
            all_lines = f.readlines()

        total_lines = len(all_lines)
        log_lines = all_lines[-lines:] if lines < total_lines else all_lines

        return {"lines": [line.rstrip() for line in log_lines], "total_lines": total_lines}
    except Exception as e:
        return {"lines": [f"Error reading log file: {str(e)}"], "total_lines": 0}


def get_service_logs_by_date_range(
    start_date: dt.datetime | None,
    end_date: dt.datetime | None,
    delta_days: int | None,
    limit: int | None,
    current_user: models.User,
    db: Session,
    table,
):
    """Get service logs within a specified date range. Admin access required.
    :param start_date: Optional start date filter (inclusive)
    :param end_date: Optional end date filter (inclusive)
    :param limit: Optional limit for number of logs to return
    :param delta_days: Optional number of days to go back in time
    :param current_user: Current authenticated admin user
    :param db: Database session
    :param table: Database table model
    :return: list of service logs within the date range ordered by run_datetime descending"""

    assert_admin(current_user)

    query = db.query(table).filter(table.run_duration.is_not(None))

    # Apply date filters
    if start_date:
        query = query.filter(table.run_datetime >= start_date)
    if end_date:
        query = query.filter(table.run_datetime <= end_date)
    if delta_days:
        start_date = dt.datetime.now() - dt.timedelta(days=delta_days)
        query = query.filter(table.run_datetime >= start_date)

    # Order by run_datetime descending (most recent first)
    query = query.order_by(table.run_datetime.desc())

    # Apply limit if specified
    if limit:
        query = query.limit(limit)

    return query.all()


def get_latest(
    current_user: models.User,
    db: Session,
    table,
):
    """Get the latest service log entry. Admin access required.
    :param current_user: Current authenticated admin user
    :param db: Database session
    :param table: Database table model
    :return: Latest service log entry"""

    assert_admin(current_user)

    latest_log = db.query(table).order_by(table.run_datetime.desc()).first()
    if not latest_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No service logs found",
        )
    return latest_log
