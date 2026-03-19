"""Unit tests for app/service_runner/routers.py."""

import datetime as dt
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from starlette import status

from app import models
from app.service_runner import routers
from app.service_runner.service_runner import ServiceRunner


# -------------------------------------------------- FIXTURES --------------------------------------------------


@pytest.fixture
def mock_runner() -> MagicMock:
    """A mocked ServiceRunner with sensible defaults."""
    runner = MagicMock(spec=ServiceRunner)
    runner.status.return_value = {
        "service_runner_status": "stopped",
        "service_running": False,
        "service_kwargs": {},
        "period_hours": 3,
        "sleep_until": None,
        "last_log": None,
    }
    return runner


# ------------------------------------------------ START SCRAPER ------------------------------------------------


class TestStartScraper:

    def test_start_scraper_success(self, mock_runner, test_admin_user) -> None:
        """Admin can start the runner; returns a detail message."""

        result = routers.start_scraper(mock_runner, test_admin_user, period_hours=2)
        mock_runner.start_runner.assert_called_once_with(period_hours=2)
        assert result == {"detail": "Service runner started (period_hours=2)"}

    def test_start_scraper_passes_kwargs(self, mock_runner, test_admin_user) -> None:
        """Extra kwargs are forwarded to start_runner."""

        routers.start_scraper(mock_runner, test_admin_user, period_hours=1, foo="bar")
        mock_runner.start_runner.assert_called_once_with(period_hours=1, foo="bar")

    def test_start_scraper_non_admin_forbidden(self, mock_runner, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.start_scraper(mock_runner, test_regular_user, period_hours=2)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        mock_runner.start_runner.assert_not_called()

    def test_start_scraper_runner_exception_raises_500(self, mock_runner, test_admin_user) -> None:
        """If start_runner raises, a 500 is propagated."""

        mock_runner.start_runner.side_effect = RuntimeError("thread error")

        with pytest.raises(HTTPException) as exc_info:
            routers.start_scraper(mock_runner, test_admin_user, period_hours=2)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "thread error" in exc_info.value.detail


# ------------------------------------------------ STOP SCRAPER ------------------------------------------------


class TestStopScraper:

    def test_stop_scraper_success(self, mock_runner, test_admin_user) -> None:
        """Admin can stop the runner; returns a detail message."""

        result = routers.stop_scraper(mock_runner, test_admin_user)
        mock_runner.stop_runner.assert_called_once()
        assert result == {"detail": "Service runner stopped"}

    def test_stop_scraper_non_admin_forbidden(self, mock_runner, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.stop_scraper(mock_runner, test_regular_user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        mock_runner.stop_runner.assert_not_called()

    def test_stop_scraper_runner_exception_raises_500(self, mock_runner, test_admin_user) -> None:
        """If stop_runner raises, a 500 is propagated."""

        mock_runner.stop_runner.side_effect = RuntimeError("cannot stop")

        with pytest.raises(HTTPException) as exc_info:
            routers.stop_scraper(mock_runner, test_admin_user)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "cannot stop" in exc_info.value.detail


# ----------------------------------------------- SCRAPER STATUS -----------------------------------------------


class TestScraperStatus:

    def test_status_success(self, mock_runner, test_admin_user) -> None:
        """Admin can retrieve runner status."""

        result = routers.scraper_status(mock_runner, test_admin_user)

        mock_runner.status.assert_called_once()
        assert result["service_runner_status"] == "stopped"

    def test_status_non_admin_forbidden(self, mock_runner, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.scraper_status(mock_runner, test_regular_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        mock_runner.status.assert_not_called()


# ----------------------------------------------- GET SERVICE LOGS (FILE) ----------------------------------------


class TestGetServiceLogs:

    def test_returns_empty_when_log_file_missing(self, test_admin_user) -> None:
        """Returns zero lines when the log file does not exist."""

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.service_runner.routers.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                result = routers.get_service_logs("nonexistent", 50, test_admin_user)

        assert result == {"lines": [], "total_lines": 0}

    def test_returns_last_n_lines_of_small_file(self, test_admin_user) -> None:
        """Returns the correct tail lines from a file under 1 MB."""

        log_lines = [f"line {i}" for i in range(20)]
        content = "\n".join(log_lines) + "\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test_service.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(content)

            with patch("app.service_runner.routers.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                result = routers.get_service_logs("test_service", 5, test_admin_user)

        assert result["total_lines"] == 20
        assert result["lines"] == log_lines[-5:]

    def test_returns_all_lines_when_fewer_than_requested(self, test_admin_user) -> None:
        """Returns all lines when the file has fewer lines than requested."""

        log_lines = ["alpha", "beta", "gamma"]
        content = "\n".join(log_lines) + "\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "svc.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(content)

            with patch("app.service_runner.routers.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                result = routers.get_service_logs("svc", 100, test_admin_user)

        assert result["lines"] == log_lines
        assert result["total_lines"] == 3

    def test_non_admin_forbidden(self, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.get_service_logs("any_service", 10, test_regular_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------- GET SERVICE LOGS BY DATE RANGE ----------------------------------------


class TestGetServiceLogsByDateRange:
    def test_no_filters_returns_all(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """Without filters, all completed logs are returned ordered by date descending."""

        result = routers.get_service_logs_by_date_range(
            start_date=None,
            end_date=None,
            delta_days=None,
            limit=None,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        assert len(result) == len(test_job_scraping_service_logs)
        # Verify descending order
        datetimes = [r.run_datetime for r in result]
        assert datetimes == sorted(datetimes, reverse=True)

    def test_start_date_filter(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """Logs before start_date are excluded."""

        start_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)
        result = routers.get_service_logs_by_date_range(
            start_date=start_date,
            end_date=None,
            delta_days=None,
            limit=None,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        assert all(r.run_datetime >= start_date for r in result)

    def test_end_date_filter(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """Logs after end_date are excluded."""

        end_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)
        result = routers.get_service_logs_by_date_range(
            start_date=None,
            end_date=end_date,
            delta_days=None,
            limit=None,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        assert all(r.run_datetime <= end_date for r in result)

    def test_delta_days_filter(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """delta_days restricts results to the last N days."""

        result = routers.get_service_logs_by_date_range(
            start_date=None,
            end_date=None,
            delta_days=2,
            limit=None,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)
        assert all(r.run_datetime >= cutoff for r in result)

    def test_limit(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """limit caps the number of returned logs."""

        result = routers.get_service_logs_by_date_range(
            start_date=None,
            end_date=None,
            delta_days=None,
            limit=2,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        assert len(result) == 2

    def test_excludes_logs_without_run_duration(self, session, test_admin_user) -> None:
        """Logs with run_duration=None (still running) are excluded."""

        log = models.JobEmailScrapingServiceLog(
            run_duration=None,
            run_datetime=dt.datetime.now(dt.timezone.utc),
            is_success=None,
            error_message=None,
            user_processed_ids=[],
            user_found_ids=[],
        )
        session.add(log)
        session.commit()

        result = routers.get_service_logs_by_date_range(
            start_date=None,
            end_date=None,
            delta_days=None,
            limit=None,
            current_user=test_admin_user,
            db=session,
            table=models.JobEmailScrapingServiceLog,
        )

        assert all(r.run_duration is not None for r in result)

    def test_non_admin_forbidden(self, session, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.get_service_logs_by_date_range(
                start_date=None,
                end_date=None,
                delta_days=None,
                limit=None,
                current_user=test_regular_user,
                db=session,
                table=models.JobEmailScrapingServiceLog,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


# -------------------------------------------------- GET LATEST --------------------------------------------------


class TestGetLatest:

    def test_returns_most_recent_log(self, session, test_admin_user, test_job_scraping_service_logs) -> None:
        """Returns the single most-recent log entry."""

        result = routers.get_latest(test_admin_user, session, models.JobEmailScrapingServiceLog)
        most_recent = max(test_job_scraping_service_logs, key=lambda l: l.run_datetime)
        assert result.id == most_recent.id

    def test_raises_404_when_no_logs(self, session, test_admin_user) -> None:
        """Raises 404 when the table has no entries."""

        with pytest.raises(HTTPException) as exc_info:
            routers.get_latest(test_admin_user, session, models.JobEmailScrapingServiceLog)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in exc_info.value.detail

    def test_non_admin_forbidden(self, session, test_regular_user) -> None:
        """Non-admin users receive 403."""

        with pytest.raises(HTTPException) as exc_info:
            routers.get_latest(test_regular_user, session, models.JobEmailScrapingServiceLog)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
