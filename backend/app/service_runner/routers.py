"""Routers for managing the service runner operations."""

import datetime as dt
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.config import settings
from app.models import User
from app.routers import assert_admin
from app.service_runner.service_runner import ServiceRunner


def start_scraper(
    service_runner: ServiceRunner,
    current_user: User,
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
    current_user: User,
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
    current_user: User,
) -> dict:
    """Get the current status service runner.
    :param service_runner: ServiceRunner instance
    :param current_user: Current authenticated user"""

    assert_admin(current_user)
    return service_runner.status()


def get_service_logs(
    logger_name: str,
    lines: int,
    current_user: User,
) -> dict:
    """Get the last N lines from the service log file efficiently.
    Uses reverse reading for large files to avoid loading the entire file into memory.
    :param lines: Number of lines to retrieve
    :param logger_name: Name of the logger / log file
    :param current_user: Current authenticated user"""

    assert_admin(current_user)

    log_file_path = os.path.join(settings.log_directory, logger_name + ".log")

    if not os.path.exists(log_file_path):
        return {"lines": [], "total_lines": 0}

    try:
        file_size = os.path.getsize(log_file_path)

        # For small files, just read the whole thing
        if file_size < 1024 * 1024:  # 1 MB threshold
            with open(log_file_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
            total_lines = len(all_lines)
            log_lines = all_lines[-lines:] if lines < total_lines else all_lines
            return {"lines": [line.rstrip() for line in log_lines], "total_lines": total_lines}

        # For large files, read from the end in chunks
        chunk_size = 8192
        collected_lines = []
        total_lines = 0

        with open(log_file_path, "rb") as f:
            # Count total lines efficiently (optional, can skip if not needed)
            for _ in f:
                total_lines += 1

            # Now read from the end to get last N lines
            f.seek(0, 2)  # Seek to end
            position = f.tell()
            buffer = b""

            while position > 0 and len(collected_lines) < lines:
                read_size = min(chunk_size, position)
                position -= read_size
                f.seek(position)
                chunk = f.read(read_size)
                buffer = chunk + buffer

                # Split into lines and keep collecting
                buffer_lines = buffer.split(b"\n")

                # If we haven't reached the start, the first element is incomplete
                if position > 0:
                    buffer = buffer_lines[0]
                    new_lines = buffer_lines[1:]
                else:
                    new_lines = buffer_lines
                    buffer = b""

                # Prepend new lines (they're in reverse order relative to file)
                collected_lines = new_lines + collected_lines

            # Take only the last N lines
            result_lines = collected_lines[-lines:] if len(collected_lines) > lines else collected_lines

            # Decode and strip
            decoded_lines = []
            for line in result_lines:
                try:
                    decoded_lines.append(line.decode("utf-8").rstrip())
                except UnicodeDecodeError:
                    decoded_lines.append(line.decode("utf-8", errors="replace").rstrip())

            # Filter out empty lines that result from splitting
            decoded_lines = [line for line in decoded_lines if line]

            return {"lines": decoded_lines, "total_lines": total_lines}

    except Exception as e:
        return {"lines": [f"Error reading log file: {str(e)}"], "total_lines": 0}


def get_service_logs_by_date_range(
    start_date: dt.datetime | None,
    end_date: dt.datetime | None,
    delta_days: int | None,
    limit: int | None,
    current_user: User,
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
    current_user: User,
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
