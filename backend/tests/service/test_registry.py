"""Unit tests for the service registry."""

import pytest
from sqlalchemy.orm import Session

from app.models import Service
from app.service import registry
from app.service.models import ServiceLog
from app.service.schemas import ServiceLogOut
from tests.base_test import BaseTest


class TestRegister(BaseTest):
    def test_register_and_get(self) -> None:
        """A registered callable can be retrieved by name."""

        fn = lambda: "ran"  # noqa: E731
        self.register_service("unit_test_service", fn)
        assert registry.get_service_callable("unit_test_service") is fn

    def test_register_overwrites(self) -> None:
        """Registering the same name twice keeps the latest callable."""

        self.register_service("dup_service", lambda: 1)
        self.register_service("dup_service", lambda: 2)
        assert registry.get_service_callable("dup_service")() == 2

    def test_get_unknown_raises_key_error(self) -> None:
        """Looking up an unregistered name raises KeyError."""

        with pytest.raises(KeyError):
            registry.get_service_callable("does_not_exist")

    def test_register_derives_display_name(self) -> None:
        """display_name defaults to a title-cased name when not provided."""

        self.register_service("my_cool_service", lambda: None)
        assert registry.SERVICE_REGISTRY["my_cool_service"].display_name == "My Cool Service"


# --------------------------------------------------- LOG VIEW ---------------------------------------------------


class TestLogView(BaseTest):
    def test_get_service_log_view_returns_pair(self) -> None:
        """The registered (model, schema) pair is returned."""

        self.register_service("view_service", log_model=ServiceLog, log_schema=ServiceLogOut)
        assert registry.get_service_log_view("view_service") == (ServiceLog, ServiceLogOut)


# -------------------------------------------------- SYNC TO DB --------------------------------------------------


class TestSyncServicesToDb(BaseTest):
    def test_inserts_missing_services_with_defaults(self, session: Session) -> None:
        """Each registered service without a row is inserted using its registration defaults."""

        registry.SERVICE_REGISTRY.clear()
        self.register_service("svc_a", lambda: None, display_name="A", run_period_hours=2, default_parameters={"x": 1})
        self.register_service("svc_b", lambda: None, run_period_hours=5)

        created = registry.sync_services_to_db(session)

        assert created == 2
        rows = {s.name: s for s in session.query(Service).all()}
        assert rows["svc_a"].display_name == "A"
        assert rows["svc_a"].run_period_hours == 2
        assert rows["svc_a"].parameters == {"x": 1}
        assert not rows["svc_a"].is_enabled
        assert rows["svc_b"].display_name == "Svc B"  # derived

    def test_idempotent_and_preserves_admin_edits(self, session: Session) -> None:
        """Re-syncing creates nothing and never overwrites an existing row."""

        registry.SERVICE_REGISTRY.clear()
        self.register_service("svc_a", lambda: None, run_period_hours=2)
        registry.sync_services_to_db(session)

        row = session.query(Service).filter(Service.name == "svc_a").one()
        row.run_period_hours = 99
        row.is_enabled = True
        session.commit()

        created = registry.sync_services_to_db(session)

        assert created == 0
        row = session.query(Service).filter(Service.name == "svc_a").one()
        assert row.run_period_hours == 99
        assert row.is_enabled is True
