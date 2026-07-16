"""Tests for the ServiceMonitor run behaviour and Error recording."""

from contextlib import nullcontext
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app import models
from app.provider_monitoring.service import service as provider_service
from app.provider_monitoring.service.service import ProviderMonitoringService
from app.provider_monitoring.service.schemas import ProviderMonitoringServiceLogOut


@pytest.fixture(autouse=True)
def _run_within_test_session(session: Session):
    """Make the service's own db_session() reuse the test's transactional session."""

    with patch.object(provider_service, "db_session", side_effect=lambda: nullcontext(session)):
        yield


def _is_success(service_log: models.ProviderMonitoringServiceLog) -> bool:
    """Derive is_success the same way the output schema does."""
    return ProviderMonitoringServiceLogOut.model_validate(service_log, from_attributes=True).is_finished


def _boom(db, logger, service_log_id=None) -> None:
    """A fetcher that always fails."""
    _ = db, logger, service_log_id
    raise RuntimeError("boom")


def _ok(db, logger, service_log_id=None) -> None:
    """A fetcher that always succeeds."""
    _ = db, logger, service_log_id
    return None


def _make_service(external_services: dict) -> ProviderMonitoringService:
    """Build an ProviderMonitoringService with its fetcher map overridden for the test."""
    service = ProviderMonitoringService()
    service.external_services = external_services
    return service


class TestServiceMonitorRun:
    def test_failed_fetcher_records_error(self, session: Session) -> None:
        """A failing fetcher records an Error linked to the run. The failure is error-level (the
        run still completes), so the derived is_success stays True."""

        service_log = _make_service({"test": [_boom]}).run()

        assert _is_success(service_log) is True

        errors = session.query(models.ServiceError).all()
        assert len(errors) == 1
        # Static message; the provider label and exception text are carried in context.
        assert errors[0].message == "Provider fetch failed."
        assert errors[0].context == {"provider": "test._boom", "error": "boom"}
        assert errors[0].provider_monitoring_service_log_id == service_log.id
        # A single fetcher failing (run continues) is an "error"-level service error
        assert errors[0].level == "error"

    def test_successful_run_records_no_error(self, session: Session) -> None:
        """A run where every fetcher succeeds is marked successful and records no Error."""

        service_log = _make_service({"test": [_ok]}).run()

        assert _is_success(service_log) is True
        assert session.query(models.ServiceError).count() == 0

    def test_fetchers_receive_run_id(self, session: Session) -> None:
        """Each fetcher is passed the current run's id so it can stamp records with service_log_id."""

        received: list[int | None] = []

        def _capture(db, logger, service_log_id=None) -> None:
            _ = db, logger
            received.append(service_log_id)

        service_log = _make_service({"a": [_capture]}).run()
        assert received == [service_log.id]

    def test_one_failure_does_not_abort_other_fetchers(self, session: Session) -> None:
        """A failing fetcher does not prevent the remaining fetchers from running."""

        calls: list[str] = []

        def _record_ok(db, logger, service_log_id=None) -> None:
            _ = db, logger, service_log_id
            calls.append("ok")

        service_log = _make_service({"a": [_boom], "b": [_record_ok]}).run()

        # The second fetcher still ran, and only the failing one produced an Error
        assert calls == ["ok"]
        # The failure is error-level (run completes), so the derived is_success stays True
        assert _is_success(service_log) is True
        assert session.query(models.ServiceError).count() == 1
