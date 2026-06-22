"""Tests for the ServiceMonitor run behaviour and Error recording."""

from unittest.mock import patch

from app import models
from app.external_service_monitoring.service import sync
from app.external_service_monitoring.service.sync import ServiceMonitor


def _boom(db) -> None:
    """A fetcher that always fails."""
    raise RuntimeError("boom")


def _ok(db) -> None:
    """A fetcher that always succeeds."""
    return None


class TestServiceMonitorRun:
    def test_failed_fetcher_records_error(self, session) -> None:
        """A failing fetcher records an Error linked to the run and marks the run unsuccessful."""

        with patch.object(sync, "EXTERNAL_SERVICES", {"test": [_boom]}):
            service_log = ServiceMonitor.run(session)

        assert service_log.is_success is False

        errors = session.query(models.Error).all()
        assert len(errors) == 1
        assert "boom" in errors[0].message
        assert errors[0].external_service_monitoring_service_log_id == service_log.id

    def test_successful_run_records_no_error(self, session) -> None:
        """A run where every fetcher succeeds is marked successful and records no Error."""

        with patch.object(sync, "EXTERNAL_SERVICES", {"test": [_ok]}):
            service_log = ServiceMonitor.run(session)

        assert service_log.is_success is True
        assert session.query(models.Error).count() == 0

    def test_one_failure_does_not_abort_other_fetchers(self, session) -> None:
        """A failing fetcher does not prevent the remaining fetchers from running."""

        calls: list[str] = []

        def _record_ok(db) -> None:
            calls.append("ok")

        with patch.object(sync, "EXTERNAL_SERVICES", {"a": [_boom], "b": [_record_ok]}):
            service_log = ServiceMonitor.run(session)

        # The second fetcher still ran, and only the failing one produced an Error
        assert calls == ["ok"]
        assert service_log.is_success is False
        assert session.query(models.Error).count() == 1
