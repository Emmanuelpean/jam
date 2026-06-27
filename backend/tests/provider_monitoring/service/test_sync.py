"""Tests for the ServiceMonitor run behaviour and Error recording."""

from app import models
from app.provider_monitoring.service.sync import ProviderMonitoringService
from app.provider_monitoring.service.schemas import ProviderMonitoringServiceLogOut


def _is_success(service_log) -> bool:
    """Derive is_success the same way the output schema does."""
    return ProviderMonitoringServiceLogOut.model_validate(service_log, from_attributes=True).is_finished


def _boom(db, logger) -> None:
    """A fetcher that always fails."""
    raise RuntimeError("boom")


def _ok(db, logger) -> None:
    """A fetcher that always succeeds."""
    return None


def _make_service(external_services: dict) -> ProviderMonitoringService:
    """Build an ProviderMonitoringService with its fetcher map overridden for the test."""
    service = ProviderMonitoringService()
    service.external_services = external_services
    return service


class TestServiceMonitorRun:
    def test_failed_fetcher_records_error(self, session) -> None:
        """A failing fetcher records an Error linked to the run. The failure is error-level (the
        run still completes), so the derived is_success stays True."""

        service_log = _make_service({"test": [_boom]}).run(session)

        assert _is_success(service_log) is True

        errors = session.query(models.ServiceError).all()
        assert len(errors) == 1
        assert "boom" in errors[0].message
        assert errors[0].provider_monitoring_service_log_id == service_log.id
        # A single fetcher failing (run continues) is an "error"-level service error
        assert errors[0].level == "error"

    def test_successful_run_records_no_error(self, session) -> None:
        """A run where every fetcher succeeds is marked successful and records no Error."""

        service_log = _make_service({"test": [_ok]}).run(session)

        assert _is_success(service_log) is True
        assert session.query(models.ServiceError).count() == 0

    def test_one_failure_does_not_abort_other_fetchers(self, session) -> None:
        """A failing fetcher does not prevent the remaining fetchers from running."""

        calls: list[str] = []

        def _record_ok(db, logger) -> None:
            calls.append("ok")

        service_log = _make_service({"a": [_boom], "b": [_record_ok]}).run(session)

        # The second fetcher still ran, and only the failing one produced an Error
        assert calls == ["ok"]
        # The failure is error-level (run completes), so the derived is_success stays True
        assert _is_success(service_log) is True
        assert session.query(models.ServiceError).count() == 1
