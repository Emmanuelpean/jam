"""Base class for all backend tests, providing helpers to create database entries."""

import datetime as dt
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app import models
from tests.utils.create_data.core import create_users
from tests.utils.create_data.utils import create_db_entries


class BaseTest:
    """Base class for all backend tests"""

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
        **kwargs,
    ) -> models.ServiceError:
        """Create a unified service-error row (not user-owned).
        :param session: database session
        :param error_type: error class name (e.g. "TimeoutError")
        :param message: error message
        :param kwargs: additional ServiceError fields (e.g. is_acknowledged, level, or a
            *_service_log_id / scraped_job_id / job_rating_id link)"""

        data = {"error_type": error_type, "message": message, **kwargs}
        return create_db_entries(session, models.ServiceError, data)[0]

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
