"""Base Selenium test class and shared test helpers.

The page/component utility classes live in the `helpers` package and are wired
onto BaseTest below. Test modules import BaseTest, MaintenanceTestBase, models and
the helper functions from this module.
"""

import json
import os
import time
from typing import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from app import models
from app.config import settings
from app.core.oauth2 import create_access_token
from helpers.admin_page_utils import AdminPageUtils
from helpers.alert_modal_utils import ConfirmModalUtils, DeleteModalUtils, LogoutModalUtils
from helpers.auth_utils import AuthentificationUtils
from helpers.column_config_sidebar_utils import ColumnConfigSidebarUtils
from helpers.command_palette_utils import CommandPaletteUtils
from helpers.dashboard_edit_utils import DashboardEditUtils
from helpers.data_modal_utils import DataModalUtils
from helpers.data_table_utils import DataTableUtils
from helpers.file_upload_utils import FileUploadUtils
from helpers.filter_sidebar_utils import FilterSidebarUtils
from helpers.followup_email_modal_utils import FollowUpEmailModalUtils
from helpers.jam_test_utils import JamTestUtils
from helpers.premium_settings_utils import PremiumSettingsUtils
from helpers.service_dashboard_utils import ServiceDashboardUtils
from helpers.toast_utils import ToastUtils
from helpers.tour_utils import TourUtils
from helpers.usage_page_utils import UsagePageUtils
from helpers.user_settings_utils import UserSettingsUtils
from tests.base_test import BaseTest as BackendBaseTest
from tests.fixtures.users import FixtureUser


class BaseTest(JamTestUtils, BackendBaseTest):
    """Base class for selenium tests"""

    _shared_backend_url = None
    _shared_frontend_url = None
    _shared_driver = None
    user: models.User  # user to use
    client = None  # authorised client
    base_utils = None  # base utils

    # Parameters needed
    page_url = "dashboard"  # url of the page to test (not including the base url)
    user_fixture = "test_regular_user"  # name of the pytest fixture providing the logged-in user

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

    # User
    user_modal_utils: DataModalUtils
    user_table_utils: DataTableUtils

    # Others
    auth_utils: AuthentificationUtils
    user_settings_utils: UserSettingsUtils
    followup_modal_utils: FollowUpEmailModalUtils
    confirm_modal_utils: ConfirmModalUtils
    delete_modal_utils: DeleteModalUtils
    logout_modal_utils: LogoutModalUtils
    premium_settings_utils: PremiumSettingsUtils
    tour_utils: TourUtils
    filter_sidebar_utils: FilterSidebarUtils
    file_upload_utils: FileUploadUtils
    service_dashboard_utils: ServiceDashboardUtils
    usage_page_utils: UsagePageUtils
    admin_page_utils: AdminPageUtils
    column_config_utils: ColumnConfigSidebarUtils
    command_palette_utils: CommandPaletteUtils
    dashboard_edit_utils: DashboardEditUtils
    toast_utils: ToastUtils

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        test_frontend_server,
        test_backend_server,
        request,
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

            # Performance logging instruments every network/rendering event and slows the whole
            # session. It is only read on failure or in CI (see _save_browser_logs), so enable the
            # heavy capture only there; keep the cheap console log always for local debugging.
            log_prefs = {"browser": "ALL"}
            if os.getenv("CI"):
                chrome_options.add_argument("--enable-logging")
                chrome_options.add_argument("--v=1")
                log_prefs["performance"] = "ALL"
            chrome_options.set_capability("goog:loggingPrefs", log_prefs)

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
            self.user: FixtureUser = request.getfixturevalue(self.user_fixture)
            self.client = self.user.client
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
                "user",
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
            self.followup_modal_utils = FollowUpEmailModalUtils(**shared_kwargs)
            self.confirm_modal_utils = ConfirmModalUtils(**shared_kwargs)
            self.delete_modal_utils = DeleteModalUtils(**shared_kwargs)
            self.logout_modal_utils = LogoutModalUtils(**shared_kwargs)
            self.premium_settings_utils = PremiumSettingsUtils(**shared_kwargs)
            self.tour_utils = TourUtils(**shared_kwargs)
            self.filter_sidebar_utils = FilterSidebarUtils(**shared_kwargs)
            self.file_upload_utils = FileUploadUtils(**shared_kwargs)
            self.service_dashboard_utils = ServiceDashboardUtils(**shared_kwargs)
            self.usage_page_utils = UsagePageUtils(**shared_kwargs)
            self.admin_page_utils = AdminPageUtils(**shared_kwargs)
            self.column_config_utils = ColumnConfigSidebarUtils(**shared_kwargs)
            self.command_palette_utils = CommandPaletteUtils(**shared_kwargs)
            self.dashboard_edit_utils = DashboardEditUtils(**shared_kwargs)
            self.toast_utils = ToastUtils(**shared_kwargs)

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
            # Get browser logs. Performance logging is only enabled in CI (see setup), so guard it.
            browser_logs = self.driver.get_log("browser")
            if "performance" in self.driver.log_types:
                performance_logs = self.driver.get_log("performance")
            else:
                performance_logs = []

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
