"""Base class for all backend tests, providing helpers to create database entries."""

import datetime as dt
import uuid
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app import models
from app.service import registry
from app.service.models import ServiceLog
from app.service.schemas import ServiceLogOut
from tests.utils.create_data.core import create_users
from tests.utils.create_data.utils import create_db_entries


class BaseTest:
    """Base class for all backend tests"""

    @pytest.fixture(autouse=True)
    def _restore_service_registry(self) -> Iterator[None]:
        """Snapshot and restore SERVICE_REGISTRY so services registered in a test don't leak to others."""

        original = dict(registry.SERVICE_REGISTRY)
        yield
        registry.SERVICE_REGISTRY.clear()
        registry.SERVICE_REGISTRY.update(original)

    @staticmethod
    def register_service(name: str, run: Callable = lambda: None, **kwargs) -> None:
        """Register a throwaway service in the runtime service registry (removed after the test).

        Distinct from create_service, which inserts a Service config row in the database: this makes the
        registry-driven service endpoints resolve `name`. log_model/log_schema default to the base
        ServiceLog view for tests that don't assert on serialisation.
        :param name: Service registry key.
        :param run: Callable invoked as run(**parameters); defaults to a no-op.
        :param kwargs: Overrides forwarded to register_service (e.g. log_model, log_schema, display_name)."""

        kwargs.setdefault("log_model", ServiceLog)
        kwargs.setdefault("log_schema", ServiceLogOut)
        registry.register_service(name, run, **kwargs)

    @staticmethod
    def create_user(session, **kwargs) -> models.User:
        """Create a user with the given fields (password hashed, plain_password attached).
        :param session: database session
        :param kwargs: User fields (e.g. email, password, is_verified, is_active)"""

        return create_users(session, [kwargs])[0]

    @staticmethod
    def get_by_id(session: Session, model, entry_id: int):
        """Get an entry of the given model by id, or None if not found.
        :param session: database session
        :param model: model class to query (e.g. models.Job)
        :param entry_id: id of the entry to fetch"""

        return session.query(model).filter(model.id == entry_id).first()

    @classmethod
    def get_user(cls, session, user_id: int) -> models.User | None:
        """Get a user by id, or None if not found.
        :param session: database session
        :param user_id: id of the user to fetch"""

        return cls.get_by_id(session, models.User, user_id)

    @staticmethod
    def create_setting(session, name: str, value: str, **kwargs) -> models.Setting:
        """Create an application setting.
        :param session: database session
        :param name: setting name (unique)
        :param value: setting value
        :param kwargs: additional Setting fields (e.g. description)"""

        return create_db_entries(session, models.Setting, {"name": name, "value": value, **kwargs})[0]

    @staticmethod
    def create_geolocation(session, **kwargs) -> models.Geolocation:
        """Create a geolocation cache row (not user-owned; `query` is unique).
        :param session: database session
        :param kwargs: additional Geolocation fields (e.g. query, latitude, longitude, city)"""

        data = {"query": f"Location {uuid.uuid4()}", **kwargs}
        return create_db_entries(session, models.Geolocation, data)[0]

    @staticmethod
    def create_email_scraping_service_log(session, **kwargs) -> models.JobEmailScrapingServiceLog:
        """Create a job email scraping service log.
        :param session: database session
        :param kwargs: additional JobEmailScrapingServiceLog fields (e.g. run_duration, run_datetime)"""

        return create_db_entries(session, models.JobEmailScrapingServiceLog, {**kwargs})[0]

    @staticmethod
    def create_job_rating_service_log(session, **kwargs) -> models.JobRatingServiceLog:
        """Create a job rating service log.
        :param session: database session
        :param kwargs: additional JobRatingServiceLog fields (e.g. run_duration, run_datetime)"""

        return create_db_entries(session, models.JobRatingServiceLog, {**kwargs})[0]

    @staticmethod
    def create_platform_stat(
        session,
        service_log: models.JobEmailScrapingServiceLog | None = None,
        name: str = "linkedin",
        **kwargs,
    ) -> models.JobEmailScrapingPlatformStat:
        """Create per-platform stats for a job email scraping run (creates a service log if none given).
        :param session: database session
        :param service_log: the run these stats belong to; a new one is created if omitted
        :param name: platform name (e.g. "linkedin", "indeed")
        :param kwargs: additional JobEmailScrapingPlatformStat fields (e.g. job_scrape_failed_ids)"""

        if service_log is None:
            service_log = BaseTest.create_email_scraping_service_log(session)
        data = {"name": name, "service_log_id": service_log.id, **kwargs}
        return create_db_entries(session, models.JobEmailScrapingPlatformStat, data)[0]

    @staticmethod
    def create_service(session, name: str = "fake_service", **kwargs) -> models.Service:
        """Create a scheduler Service config row (not user-owned).
        :param session: database session
        :param name: unique service name
        :param kwargs: additional Service fields (e.g. run_period_hours, parameters, is_enabled, next_run_at)"""

        data = {
            "name": name,
            "display_name": name.replace("_", " ").title(),
            "run_period_hours": 3.0,
            "parameters": {},
            "is_enabled": True,
            "is_running": False,
            **kwargs,
        }
        return create_db_entries(session, models.Service, data)[0]

    @staticmethod
    def create_service_error(
        session,
        error_type: str = "RuntimeError",
        message: str = "boom",
        traceback: str = "Traceback (most recent call last):\n  ...\nRuntimeError: boom",
        **kwargs,
    ) -> models.ServiceError:
        """Create a unified service-error row (not user-owned).
        :param session: database session
        :param error_type: error class name (e.g. "TimeoutError")
        :param message: error message
        :param traceback: error traceback
        :param kwargs: additional ServiceError fields (e.g. is_acknowledged, level, or a
            *_service_log_id / scraped_job_id / job_rating_id link)"""

        data = {"error_type": error_type, "message": message, "traceback": traceback, **kwargs}
        return create_db_entries(session, models.ServiceError, data)[0]

    @staticmethod
    def create_anthropic_usage(session, **kwargs) -> models.AnthropicDailyUsage:
        """Create a day of Anthropic spend (USD, not user-owned).
        :param session: database session
        :param kwargs: AnthropicDailyUsage fields (e.g. date, usage_usd)"""

        data = {"date": dt.datetime.now(dt.timezone.utc).date(), "usage_usd": 10.0, **kwargs}
        return create_db_entries(session, models.AnthropicDailyUsage, data)[0]

    @staticmethod
    def create_apify_usage(session, **kwargs) -> models.ApifyDailyUsage:
        """Create a day of Apify usage (USD, not user-owned).
        :param session: database session
        :param kwargs: ApifyDailyUsage fields (e.g. date, usage_usd)"""

        data = {"date": dt.datetime.now(dt.timezone.utc).date(), "usage_usd": 5.0, **kwargs}
        return create_db_entries(session, models.ApifyDailyUsage, data)[0]

    @staticmethod
    def create_apify_balance(session, **kwargs) -> models.ApifyBalance:
        """Create an Apify cycle balance snapshot (USD, not user-owned).
        :param session: database session
        :param kwargs: ApifyBalance fields (e.g. limit_usd)"""

        data = {"limit_usd": 100.0, **kwargs}
        return create_db_entries(session, models.ApifyBalance, data)[0]

    @staticmethod
    def create_brightdata_usage(session, **kwargs) -> models.BrightdataDailyUsage:
        """Create a day of Bright Data spend (USD) for one dataset (not user-owned).
        :param session: database session
        :param kwargs: BrightdataDailyUsage fields (e.g. date, dataset, usage_usd)"""

        data = {"date": dt.datetime.now(dt.timezone.utc).date(), "dataset": "linkedin", "usage_usd": 3.0, **kwargs}
        return create_db_entries(session, models.BrightdataDailyUsage, data)[0]

    @staticmethod
    def create_brightdata_balance(session, **kwargs) -> models.BrightdataBalance:
        """Create a Bright Data balance snapshot (USD, not user-owned).
        :param session: database session
        :param kwargs: BrightdataBalance fields (e.g. balance_usd, pending_costs_usd)"""

        data = {"balance_usd": 50.0, "pending_costs_usd": 2.0, **kwargs}
        return create_db_entries(session, models.BrightdataBalance, data)[0]

    @staticmethod
    def create_stripe_income(session, **kwargs) -> models.StripeDailyIncome:
        """Create a day of Stripe income (GBP, not user-owned).
        :param session: database session
        :param kwargs: StripeDailyIncome fields (e.g. date, gross_gbp, net_gbp)"""

        data = {"date": dt.datetime.now(dt.timezone.utc).date(), "gross_gbp": 100.0, "net_gbp": 80.0, **kwargs}
        return create_db_entries(session, models.StripeDailyIncome, data)[0]

    @staticmethod
    def _create_maintenance_setting(session: Session, minutes_offset: int) -> models.Setting:
        """Insert a maintenance_scheduled_at setting with a timestamp offset from now.
        A negative offset puts the time in the past (maintenance active).
        A positive offset puts the time in the future (scheduled but not yet active).
        """
        scheduled_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes_offset)
        return BaseTest.create_setting(session, "maintenance_scheduled_at", scheduled_at.isoformat())

    def check_output(
        self,
        test_data: Any,
        response_data: list[dict] | dict,
        out_schema=None,
    ):
        """Check that the output of a test matches the test data."""
        if isinstance(test_data, list) and isinstance(response_data, list):
            assert len(test_data) == len(response_data)
            for d1, d2 in zip(test_data, response_data):
                return self.check_output(d1, d2, out_schema)

        if isinstance(response_data, dict) and out_schema is not None:
            response_data = out_schema(**response_data)

        if isinstance(test_data, dict):
            items = test_data.items()
        else:
            items = vars(test_data).items()

        for key, value in items:
            if key[0] != "_" and key in response_data:
                response_value = getattr(response_data, key)
                if isinstance(value, models.Base) or isinstance(value, list):
                    self.check_output(value, response_value, out_schema)
                elif key == "date" and isinstance(value, str):
                    if isinstance(response_value, dt.datetime):
                        parsed_value = dt.datetime.fromisoformat(value)
                        if response_value.tzinfo is not None and parsed_value.tzinfo is None:
                            parsed_value = parsed_value.replace(tzinfo=dt.timezone.utc)
                        elif response_value.tzinfo is None and parsed_value.tzinfo is not None:
                            parsed_value = parsed_value.replace(tzinfo=None)
                        assert parsed_value == response_value
                    else:
                        assert value == response_value
                else:
                    try:
                        assert value == response_value
                    except Exception:
                        print(value)
                        print(response_value)
                        raise AssertionError

        return None
