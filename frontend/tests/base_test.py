"""Base Selenium test class and shared test helpers.

The page/component utility classes live in the `helpers` package and are wired
onto BaseTest below. Test modules import BaseTest, MaintenanceTestBase, models and
the helper functions from this module.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from app import models
from app.config import settings
from app.core.oauth2 import create_access_token

from helpers.base_utils import BaseUtils
from helpers.data_modal_utils import DataModalUtils
from helpers.data_table_utils import DataTableUtils
from helpers.auth_utils import AuthentificationUtils
from helpers.user_settings_utils import UserSettingsUtils
from helpers.followup_email_modal_utils import FollowUpEmailModalUtils
from helpers.alert_modal_utils import ConfirmModalUtils, DeleteModalUtils, LogoutModalUtils
from helpers.premium_settings_utils import PremiumSettingsUtils
from helpers.tour_utils import TourUtils

# Re-exported for tests that import these helpers from base_test.
from helpers.formatting import format_file_size, contiguous_subdicts, format_field

__all__ = ["BaseTest", "MaintenanceTestBase", "models", "format_file_size", "contiguous_subdicts", "format_field"]


class BaseTest(BaseUtils):
    """Base class for selenium tests"""

    _shared_backend_url = None
    _shared_frontend_url = None
    _shared_driver = None
    user: models.User  # user to use
    client = None  # authorised client
    base_utils = None  # base utils

    # Parameters needed
    page_url = "dashboard"  # url of the page to test (not including the base url)
    user_index = 1  # index of the user to use for the test

    _test_name = ""

    # Company
    company_modal_utils: DataModalUtils
    company_table_utils: DataTableUtils

    # Aggregator
    aggregator_modal_utils: DataModalUtils
    aggregator_table_utils: DataTableUtils

    # Keyword
    keyword_modal_utils: DataModalUtils
    keyword_table_utils: DataTableUtils

    # Person
    person_modal_utils: DataModalUtils
    person_table_utils: DataTableUtils

    # Job
    job_modal_utils: DataModalUtils
    job_table_utils: DataTableUtils

    # Interview
    interview_modal_utils: DataModalUtils
    interview_table_utils: DataTableUtils

    # Job Application Update
    jobApplicationUpdate_modal_utils: DataModalUtils
    jobApplicationUpdate_table_utils: DataTableUtils

    # Speculative Application
    speculativeApplication_modal_utils: DataModalUtils
    speculativeApplication_table_utils: DataTableUtils

    # Scraped Job
    scrapedJob_modal_utils: DataModalUtils
    scrapedJob_table_utils: DataTableUtils

    # Job Email
    jobEmail_modal_utils: DataModalUtils
    jobEmail_table_utils: DataTableUtils

    # Scraping Filter
    scrapingExclusionFilter_modal_utils: DataModalUtils
    scrapingExclusionFilter_table_utils: DataTableUtils

    # Settings
    setting_modal_utils: DataModalUtils
    setting_table_utils: DataTableUtils

    # Others
    auth_utils: AuthentificationUtils
    user_settings_utils: UserSettingsUtils
    followup_modal: FollowUpEmailModalUtils
    confirm_modal: ConfirmModalUtils
    delete_modal: DeleteModalUtils
    logout_modal: LogoutModalUtils
    premium_settings_utils: PremiumSettingsUtils
    tour_utils: TourUtils

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        test_frontend_server,
        test_backend_server,
        request,
        test_users,
        authorised_clients,
        session,
    ) -> Generator[None, None, None]:
        """Set up the test environment before each test with test data"""

        self._test_name = request.node.name
        try:

            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
                "protocol_handler": {"excluded_schemes": {"mailto": True}},
                "intl.accept_languages": "en-GB",
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1960,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--lang=en-GB")

            # Enable verbose logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            # Set timezone using CDP
            self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/London"})
            # Set locale using CDP
            self.driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en-GB"})

            # Frontend/Backend
            self.frontend_base_url = test_frontend_server
            self.backend_base_url = test_backend_server

            # Client/User
            self.user = test_users[self.user_index]
            self.client = authorised_clients[self.user_index]
            self.db = session

            modal_entities = [
                "company",
                "aggregator",
                "keyword",
                "person",
                "job",
                "interview",
                "jobApplicationUpdate",
                "speculativeApplication",
                "scrapedJob",
                "jobEmail",
                "scrapingExclusionFilter",
                "scrapingFavouriteFilter",
                "setting",
            ]

            shared_kwargs = {
                "driver": self.driver,
                "frontend_base_url": self.frontend_base_url,
                "backend_base_url": self.backend_base_url,
                "db": self.db,
                "client": self.client,
            }
            for name in modal_entities:
                setattr(self, f"{name}_modal_utils", DataModalUtils(entry_type=name, **shared_kwargs))
            for name in modal_entities:
                setattr(self, f"{name}_table_utils", DataTableUtils(entry_type=name, **shared_kwargs))

            self.auth_utils = AuthentificationUtils(**shared_kwargs)
            self.user_settings_utils = UserSettingsUtils(**shared_kwargs)
            self.followup_modal = FollowUpEmailModalUtils(**shared_kwargs)
            self.confirm_modal = ConfirmModalUtils(**shared_kwargs)
            self.delete_modal = DeleteModalUtils(**shared_kwargs)
            self.logout_modal = LogoutModalUtils(**shared_kwargs)
            self.premium_settings_utils = PremiumSettingsUtils(**shared_kwargs)
            self.tour_utils = TourUtils(**shared_kwargs)

            self.driver.get(self.frontend_base_url)
            self.setup_function(request)

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self._save_browser_logs(failed=True)
                    self.driver.quit()
                except Exception:
                    pass
            raise
        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                # Check if test failed
                test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

                # Save logs on failure or in CI (always in CI for debugging)
                if test_failed or os.getenv("CI"):
                    self._save_browser_logs(failed=test_failed)
                    self._save_page_screenshot(failed=test_failed)
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def setup_function(self, request) -> None:
        """Function to run before each test - can be overridden in subclasses"""
        pass

    def _save_browser_logs(self, failed: bool = False) -> None:
        """Save browser console logs to file"""
        try:
            # Get browser logs
            browser_logs = self.driver.get_log("browser")
            performance_logs = self.driver.get_log("performance")

            # Create filename with test name and timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            # Save browser console logs
            browser_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_browser.log"
            with open(browser_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Status: {status_string}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write("=" * 80 + "\n\n")

                for entry in browser_logs:
                    f.write(f"[{entry['level']}] {entry['timestamp']}: {entry['message']}\n")

            # Save performance logs (network requests)
            perf_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_network.log"
            with open(perf_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write("Network Performance Logs\n")
                f.write("=" * 80 + "\n\n")

                for entry in performance_logs:
                    try:
                        log_entry = json.loads(entry["message"])
                        # Filter for network events
                        if "Network" in log_entry.get("message", {}).get("method", ""):
                            f.write(json.dumps(log_entry, indent=2) + "\n")
                    except Exception:
                        pass

            print(f"✅ Saved browser logs to {browser_log_file}")

        except Exception as e:
            print(f"⚠️ Could not save browser logs: {e}")

    def _save_page_screenshot(self, failed: bool = False) -> None:
        """Save screenshot and page HTML of current page"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            screenshot_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_file))
            print(f"✅ Saved screenshot to {screenshot_file}")

            html_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"✅ Saved page source to {html_file}")

        except Exception as e:
            print(f"⚠️ Could not save screenshot/page source: {e}")

    def login(self, user: models.User | None = None) -> None:
        """Log in by generating a JWT token directly and injecting it into localStorage."""

        if not user:
            user = self.user
        if not user:
            raise AssertionError("No user provided")

        # Generate JWT directly — no HTTP call, no bcrypt verification
        token = create_access_token(
            data={"user_id": user.id},
            token_version=user.token_version,
        )

        # Inject token into localStorage — browser is already on the same origin from setup_method
        self.driver.execute_script(f'window.localStorage.setItem("token", "{token}");')

        self.driver.get(f"{self.frontend_base_url}/{self.page_url}")
        self.wait_for_page(self.page_url)
        self.wait_for_disappear("loading-spinner")

    def refresh(self) -> None:
        """Refresh the page"""

        self.driver.refresh()
        self.wait_for_disappear("loading-spinner")

    # ---------------------------------------------------- DATABASE ----------------------------------------------------

    @property
    def db_user(self) -> models.User:
        """Get the user from the database"""

        self.db.expire_all()
        user = self.db.query(models.User).filter(models.User.id == self.user.id).first()
        assert user
        return user

    def verify_user_in_database(self, email: str) -> list[models.User]:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

    def _make_company(self, **kwargs) -> models.Company:
        """Create and persist a Company owned by the current test user."""

        defaults = {
            "name": "Test Company",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        company = models.Company(**defaults)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def _make_person(self, **kwargs) -> models.Person:
        """Create and persist a Person owned by the current test user."""

        defaults = {
            "first_name": "Test",
            "last_name": "Person",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        person = models.Person(**defaults)
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def _make_job(self, **kwargs) -> models.Job:
        """Create and persist a Job owned by the current test user."""

        defaults = {
            "title": "Test Job",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        job = models.Job(**defaults)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _make_speculative_application(self, company: models.Company, **kwargs) -> models.SpeculativeApplication:
        """Create and persist a SpeculativeApplication owned by the current test user."""

        defaults = {
            "company_id": company.id,
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        application = models.SpeculativeApplication(**defaults)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def _make_aggregator(self, **kwargs) -> models.Aggregator:
        """Create and persist an Aggregator owned by the current test user."""

        defaults = {
            "name": "Test Aggregator",
            "url": "https://www.test-aggregator.com",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        aggregator = models.Aggregator(**defaults)
        self.db.add(aggregator)
        self.db.commit()
        self.db.refresh(aggregator)
        return aggregator

    def _make_service_log(self, **kwargs) -> models.JobEmailScrapingServiceLog:
        """Create and persist a JobEmailScrapingServiceLog."""

        defaults = {
            "run_datetime": datetime.now(timezone.utc),
        }
        defaults.update(kwargs)
        service_log = models.JobEmailScrapingServiceLog(**defaults)
        self.db.add(service_log)
        self.db.commit()
        self.db.refresh(service_log)
        return service_log

    def _make_service_error(
        self, service_log: models.JobEmailScrapingServiceLog | None = None, **kwargs
    ) -> models.JobEmailScrapingServiceError:
        """Create and persist a JobEmailScrapingServiceError linked to the given (or a new) service log."""

        if service_log is None:
            service_log = self._make_service_log()
        defaults = {
            "error_type": "ConnectionError",
            "message": "Test service error",
            "traceback": "Traceback (most recent call last): ...",
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        service_error = models.JobEmailScrapingServiceError(**defaults)
        self.db.add(service_error)
        self.db.commit()
        self.db.refresh(service_error)
        return service_error

    def _make_platform_stat(
        self, service_log: models.JobEmailScrapingServiceLog | None = None, **kwargs
    ) -> models.JobEmailScrapingPlatformStat:
        """Create and persist a JobEmailScrapingPlatformStat linked to the given (or a new) service log."""

        if service_log is None:
            service_log = self._make_service_log()
        defaults = {
            "name": "linkedin",
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        platform_stat = models.JobEmailScrapingPlatformStat(**defaults)
        self.db.add(platform_stat)
        self.db.commit()
        self.db.refresh(platform_stat)
        return platform_stat

    def _make_scraped_job(
        self, service_log: models.JobEmailScrapingServiceLog | None = None, **kwargs
    ) -> models.ScrapedJob:
        """Create and persist a ScrapedJob owned by the current test user."""

        if service_log is None:
            service_log = self._make_service_log()
        defaults = {
            "external_job_id": str(uuid.uuid4()),
            "platform": "linkedin",
            "owner_id": self.user.id,
            "is_processed": True,
            "is_scraped": True,
            "title": "Test Job",
            "url": "test.com",
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        job = models.ScrapedJob(**defaults)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _make_qualifications(self, **kwargs) -> models.UserQualification:
        """Create and persist a UserQualification owned by the current test user."""

        defaults = {
            "owner_id": self.user.id,
            "experience": "Test experience",
        }
        defaults.update(kwargs)
        qualification = models.UserQualification(**defaults)
        self.db.add(qualification)
        self.db.commit()
        self.db.refresh(qualification)
        return qualification

    def _create_job_rating(self, scraped_job: models.ScrapedJob, **kwargs) -> models.JobRating:
        """Create and persist a JobRating linked to the given scraped job."""

        qualification = self._make_qualifications()
        defaults = {
            "owner_id": self.user.id,
            "scraped_job_id": scraped_job.id,
            "user_qualification_id": qualification.id,
        }
        defaults.update(kwargs)
        rating = models.JobRating(**defaults)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def _make_rating_service_log(self, **kwargs) -> models.JobRatingServiceLog:
        """Create and persist a JobRatingServiceLog."""

        defaults = {
            "run_datetime": datetime.now(timezone.utc),
        }
        defaults.update(kwargs)
        rating_log = models.JobRatingServiceLog(**defaults)
        self.db.add(rating_log)
        self.db.commit()
        self.db.refresh(rating_log)
        return rating_log

    def _make_job_email(
        self,
        scraped_jobs: list | None = None,
        service_log: models.JobEmailScrapingServiceLog | None = None,
        **kwargs,
    ) -> models.JobEmail:
        """Create and persist a JobEmail owned by the current test user."""

        if service_log is None:
            service_log = self._make_service_log()
        defaults = {
            "external_email_id": str(uuid.uuid4()),
            "subject": "Test Job Alert Email",
            "sender": "alerts@linkedin.com",
            "date_received": datetime.now(timezone.utc),
            "platform": "linkedin",
            "body": "Test email body",
            "owner_id": self.user.id,
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        email = models.JobEmail(**defaults)
        if scraped_jobs:
            email.jobs = scraped_jobs
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    def _create_setting(self, **kwargs) -> models.Setting:
        """Create a new setting entry"""

        setting = models.Setting(**kwargs)
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def _create_job(self, title: str = "Test Job", **kwargs) -> models.Job:
        """Create and persist a Job owned by the current test user."""

        job = models.Job(owner_id=self.user.id, title=title, **kwargs)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _create_geolocated_job(self, title: str, city: str, country: str, lat: float, lng: float) -> models.Job:
        """Create a Job linked to a geocoded location so it appears as a marker on the map."""

        geo = models.Geolocation(
            query=f"{city}, {country} ({title})",  # query is unique-constrained
            latitude=lat,
            longitude=lng,
            city=city,
            country=country,
        )
        self.db.add(geo)
        self.db.flush()
        return self._create_job(title=title, location=f"{city}, {country}", geolocation_id=geo.id)

    def _create_interview(self, job_id: int, date: datetime, **kwargs) -> models.Interview:
        """Create and persist an Interview for the given job."""

        defaults = {"type": "HR"}
        defaults.update(kwargs)
        interview = models.Interview(owner_id=self.user.id, job_id=job_id, date=date, **defaults)
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def _create_update(self, job_id: int, date: datetime, **kwargs) -> models.JobApplicationUpdate:
        """Create and persist a JobApplicationUpdate for the given job."""

        defaults = {"type": "received"}
        defaults.update(kwargs)
        update = models.JobApplicationUpdate(owner_id=self.user.id, job_id=job_id, date=date, **defaults)
        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)
        return update

    def _create_scraped_job(self, title: str = "Scraped Job", **kwargs) -> models.ScrapedJob:
        """Create and persist a ScrapedJob owned by the current test user.

        A JobEmailScrapingServiceLog is created automatically if service_log_id is not provided.
        external_job_id defaults to a per-instance sequential value so multiple calls within
        one test always produce unique IDs without any manual bookkeeping.
        """

        if not hasattr(self, "_scraped_job_seq"):
            self._scraped_job_seq = 0
        self._scraped_job_seq += 1

        if "service_log_id" not in kwargs:
            log = models.JobEmailScrapingServiceLog(run_datetime=datetime.now(timezone.utc))
            self.db.add(log)
            self.db.flush()
            kwargs["service_log_id"] = log.id

        external_job_id = kwargs.pop("external_job_id", f"ext-{self._scraped_job_seq}")
        platform = kwargs.pop("platform", "Indeed")

        scraped_job = models.ScrapedJob(
            owner_id=self.user.id,
            external_job_id=external_job_id,
            platform=platform,
            title=title,
            **kwargs,
        )
        self.db.add(scraped_job)
        self.db.commit()
        self.db.refresh(scraped_job)
        return scraped_job

    def _create_scraped_job_with_failed_rating(self, title: str = "Failed Rating Job", **kwargs) -> models.ScrapedJob:
        """Create a scraped job that has a failed JobRating (is_success=False)."""

        job = self._create_scraped_job(title=title, **kwargs)
        self._create_job_rating(job, is_success=False, llm_model="XX")
        return job

    def _create_favourite_filter(
        self, filter_type: str, operator: str, value: str, **kwargs
    ) -> models.ScrapingFavouriteFilter:
        """Create and persist a ScrapingFavouriteFilter owned by the current test user."""

        fav = models.ScrapingFavouriteFilter(
            owner_id=self.user.id,
            type=filter_type,
            operator=operator,
            value=value,
            **kwargs,
        )
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def _create_confirmation_link(self, is_used: bool = False, **kwargs) -> models.ForwardingConfirmationLink:
        """Create and persist a forwarding confirmation link owned by the current test user."""

        link = models.ForwardingConfirmationLink(
            email_external_id="ext_test_123",
            url="https://mail.google.com/confirm/abc123",
            platform="gmail",
            is_used=is_used,
            owner_id=self.user.id,
            **kwargs,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link


class MaintenanceTestBase(BaseTest):
    """Shared helpers for maintenance tests."""

    _setting_id = None

    def _set_maintenance_scheduled_at(self, iso_timestamp: str) -> None:
        """Create or update the maintenance_scheduled_at setting via the API."""

        if self._setting_id is None:
            response = self.client.post("/settings/", json={"name": "maintenance_scheduled_at", "value": iso_timestamp})
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = self.client.put(f"/settings/{self._setting_id}", json={"value": iso_timestamp})
            assert response.status_code == 200

    def _clear_maintenance_scheduled_at(self) -> None:
        """Delete the maintenance_scheduled_at setting if it exists."""

        if self._setting_id is not None:
            self.client.delete(f"/settings/{self._setting_id}")
            self._setting_id = None

    @staticmethod
    def _get_future_timestamp(minutes: int | float = 30) -> str:
        """Get an ISO 8601 timestamp for a time in the future."""

        future_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        return future_time.isoformat()

    @staticmethod
    def _get_past_timestamp(minutes: int | float = 5) -> str:
        """Get an ISO 8601 timestamp for a time in the past."""

        past_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return past_time.isoformat()
