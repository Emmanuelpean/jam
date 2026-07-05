"""Base class for all backend tests, providing helpers to create database entries."""

import datetime as dt
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.core.models import TokenType
from app.core.utils import generate_token
from tests.utils.create_data.core import create_users
from tests.utils.create_data.utils import create_db_entries


class BaseTest:
    """Base class for all backend tests.

    Provides utility methods to create database entries directly, so individual tests can set up
    only the data they need instead of relying on shared fixtures.
    """

    @staticmethod
    def create_user(session, **kwargs) -> models.User:
        """Create a user with the given fields (password hashed, plain_password attached).
        :param session: database session
        :param kwargs: User fields (e.g. email, password, is_verified, is_active)"""

        return create_users(session, [kwargs])[0]

    @staticmethod
    def get_by_id(session, model, entry_id: int):
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
    def create_user_qualification(session, owner, **kwargs) -> models.UserQualification:
        """Create a user qualification owned by the given user.
        :param session: database session
        :param owner: user that owns the qualification
        :param kwargs: additional UserQualification fields (e.g. education, experience)"""

        return create_db_entries(session, models.UserQualification, {"owner_id": owner.id, **kwargs})[0]

    @staticmethod
    def create_job(session, owner, **kwargs) -> models.Job:
        """Create a job owned by the given user.
        :param session: database session
        :param owner: user that owns the job
        :param kwargs: additional Job fields (e.g. title, company_id)"""

        data = {"owner_id": owner.id, "title": "Test Job", **kwargs}
        return create_db_entries(session, models.Job, data)[0]

    @staticmethod
    def create_person(session, owner, **kwargs) -> models.Person:
        """Create a person owned by the given user.
        :param session: database session
        :param owner: user that owns the person
        :param kwargs: additional Person fields (e.g. first_name, last_name, email)"""

        data = {"owner_id": owner.id, "first_name": "John", "last_name": "Doe", **kwargs}
        return create_db_entries(session, models.Person, data)[0]

    @staticmethod
    def create_company(session, owner, **kwargs) -> models.Company:
        """Create a company owned by the given user.
        :param session: database session
        :param owner: user that owns the company
        :param kwargs: additional Company fields (e.g. name, url, description)"""

        data = {"owner_id": owner.id, "name": "Acme Corp", **kwargs}
        return create_db_entries(session, models.Company, data)[0]

    @staticmethod
    def create_geolocation(session, **kwargs) -> models.Geolocation:
        """Create a geolocation cache row (not user-owned; `query` is unique).
        :param session: database session
        :param kwargs: additional Geolocation fields (e.g. query, latitude, longitude, city)"""

        data = {"query": f"Location {uuid.uuid4()}", **kwargs}
        return create_db_entries(session, models.Geolocation, data)[0]

    @staticmethod
    def create_aggregator(session, owner, **kwargs) -> models.Aggregator:
        """Create an aggregator owned by the given user.
        :param session: database session
        :param owner: user that owns the aggregator
        :param kwargs: additional Aggregator fields (e.g. name, url)"""

        data = {"owner_id": owner.id, "name": "LinkedIn", "url": "https://linkedin.com", **kwargs}
        return create_db_entries(session, models.Aggregator, data)[0]

    @staticmethod
    def create_keyword(session, owner, name: str = "Python", **kwargs) -> models.Keyword:
        """Create a keyword owned by the given user.
        :param session: database session
        :param owner: user that owns the keyword
        :param name: keyword name
        :param kwargs: additional Keyword fields"""

        data = {"owner_id": owner.id, "name": name, **kwargs}
        return create_db_entries(session, models.Keyword, data)[0]

    @staticmethod
    def create_interview(session, owner, job, **kwargs) -> models.Interview:
        """Create an interview for the given job.
        :param session: database session
        :param owner: user that owns the interview
        :param job: Job the interview belongs to
        :param kwargs: additional Interview fields (e.g. type, note, date)"""

        data = {"owner_id": owner.id, "job_id": job.id, "type": "technical", **kwargs}
        return create_db_entries(session, models.Interview, data)[0]

    @staticmethod
    def create_job_application_update(session, owner, job, **kwargs) -> models.JobApplicationUpdate:
        """Create a job application update for the given job.
        :param session: database session
        :param owner: user that owns the update
        :param job: Job the update belongs to
        :param kwargs: additional JobApplicationUpdate fields (e.g. type, note, date)"""

        data = {"owner_id": owner.id, "job_id": job.id, "type": "received", **kwargs}
        return create_db_entries(session, models.JobApplicationUpdate, data)[0]

    @staticmethod
    def create_speculative_application(session, owner, company, **kwargs) -> models.SpeculativeApplication:
        """Create a speculative application against the given company.
        :param session: database session
        :param owner: user that owns the application
        :param company: Company the application targets
        :param kwargs: additional SpeculativeApplication fields (e.g. note, contact_email, date)"""

        data = {"owner_id": owner.id, "company_id": company.id, **kwargs}
        return create_db_entries(session, models.SpeculativeApplication, data)[0]

    @staticmethod
    def create_file(session, owner, **kwargs) -> models.File:
        """Create a file (e.g. CV or cover letter) owned by the given user.
        :param session: database session
        :param owner: user that owns the file
        :param kwargs: additional File fields (e.g. filename, content, type, size, file_type)"""

        data = {
            "owner_id": owner.id,
            "filename": "cv.pdf",
            "content": "base64content",
            "type": "application/pdf",
            "size": 1024,
            **kwargs,
        }
        return create_db_entries(session, models.File, data)[0]

    @staticmethod
    def create_forwarding_confirmation_link(session, owner, **kwargs) -> models.ForwardingConfirmationLink:
        """Create a forwarding confirmation link owned by the given user.
        :param session: database session
        :param owner: user that owns the link
        :param kwargs: additional ForwardingConfirmationLink fields (e.g. url, platform, is_used)"""

        data = {
            "owner_id": owner.id,
            "email_external_id": "ext_123",
            "url": "https://example.com/confirm",
            "platform": "gmail",
            **kwargs,
        }
        return create_db_entries(session, models.ForwardingConfirmationLink, data)[0]

    @staticmethod
    def create_service_log(session, **kwargs) -> models.JobEmailScrapingServiceLog:
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
        session, error_type: str = "RuntimeError", message: str = "boom", **kwargs
    ) -> models.ServiceError:
        """Create a unified service-error row (not user-owned).
        :param session: database session
        :param error_type: error class name (e.g. "TimeoutError")
        :param message: error message
        :param kwargs: additional ServiceError fields (e.g. is_acknowledged, level, or a
            *_service_log_id / scraped_job_id / job_rating_id link)"""

        data = {"error_type": error_type, "message": message, **kwargs}
        return create_db_entries(session, models.ServiceError, data)[0]

    @classmethod
    def create_job_email(cls, session, owner, service_log=None, **kwargs) -> models.JobEmail:
        """Create a job alert email owned by the given user.
        :param session: database session
        :param owner: user that owns the job email
        :param service_log: JobEmailScrapingServiceLog the email belongs to; created if not given
        :param kwargs: additional JobEmail fields (e.g. subject, sender, platform)"""

        if service_log is None:
            service_log = cls.create_service_log(session)
        data = {
            "owner_id": owner.id,
            "service_log_id": service_log.id,
            "external_email_id": str(uuid.uuid4()),
            "subject": "Test Job Alert",
            "sender": "jobs@linkedin.com",
            "date_received": dt.datetime.now(dt.timezone.utc),
            "platform": "linkedin",
            "body": "Test email body",
            **kwargs,
        }
        return create_db_entries(session, models.JobEmail, data)[0]

    @classmethod
    def create_scraped_job(cls, session, owner, service_log=None, **kwargs) -> models.ScrapedJob:
        """Create a scraped job owned by the given user.
        :param session: database session
        :param owner: user that owns the scraped job
        :param service_log: JobEmailScrapingServiceLog the job belongs to; created if not given
        :param kwargs: additional ScrapedJob fields (e.g. title, platform, external_job_id)"""

        if service_log is None:
            service_log = cls.create_service_log(session)
        data = {
            "owner_id": owner.id,
            "service_log_id": service_log.id,
            "external_job_id": str(uuid.uuid4()),
            "platform": "linkedin",
            **kwargs,
        }
        return create_db_entries(session, models.ScrapedJob, data)[0]

    @classmethod
    def create_job_rating(cls, session, owner, scraped_job=None, user_qualification=None, **kwargs) -> models.JobRating:
        """Create a job rating owned by the given user for a scraped job and user qualification.
        :param session: database session
        :param owner: user that owns the job rating
        :param scraped_job: ScrapedJob being rated; created if not given
        :param user_qualification: UserQualification used to rate the job; created if not given
        :param kwargs: additional JobRating fields (e.g. overall_score, llm_model)"""

        if scraped_job is None:
            scraped_job = cls.create_scraped_job(session, owner)
        if user_qualification is None:
            user_qualification = cls.create_user_qualification(session, owner, experience="Test")
        data = {
            "owner_id": owner.id,
            "scraped_job_id": scraped_job.id,
            "user_qualification_id": user_qualification.id,
            "llm_model": "claude",
            **kwargs,
        }
        return create_db_entries(session, models.JobRating, data)[0]

    @staticmethod
    def create_scraping_exclusion_filter(session, owner, **kwargs) -> models.ScrapingExclusionFilter:
        """Create a scraping exclusion filter owned by the given user.
        :param session: database session
        :param owner: user that owns the filter
        :param kwargs: additional filter fields (e.g. type, operator, value, is_active)"""

        data = {"owner_id": owner.id, "type": "title", "operator": "contains", "value": "Some", **kwargs}
        return create_db_entries(session, models.ScrapingExclusionFilter, data)[0]

    @staticmethod
    def create_scraping_favourite_filter(session, owner, **kwargs) -> models.ScrapingFavouriteFilter:
        """Create a scraping favourite filter owned by the given user.
        :param session: database session
        :param owner: user that owns the filter
        :param kwargs: additional filter fields (e.g. type, operator, value, is_active)"""

        data = {"owner_id": owner.id, "type": "title", "operator": "contains", "value": "Python", **kwargs}
        return create_db_entries(session, models.ScrapingFavouriteFilter, data)[0]

    @staticmethod
    def get_token(session, owner, token_type) -> models.UserToken | None:
        """Get the most recent token of the given type for the given user.
        :param session: database session
        :param owner: user that owns the token
        :param token_type: TokenType to filter by"""

        return (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == owner.id)
            .filter(models.UserToken.token_type == token_type)
            .order_by(models.UserToken.created_at.desc())
            .first()
        )

    @staticmethod
    def create_token(session, owner, token_type: TokenType, **kwargs) -> tuple[str, models.UserToken]:
        """Generate a token of the given type for the given user (replaces existing tokens of that type).
        :param session: database session
        :param owner: user that owns the token
        :param token_type: TokenType to generate
        :param kwargs: additional generate_token args (e.g. pending_email)
        :return: tuple of (plain_token, UserToken)"""

        return generate_token(owner.id, token_type, session, **kwargs)

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
