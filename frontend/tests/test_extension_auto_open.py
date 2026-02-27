"""Tests for the Chrome extension autoOpenWith feature.

When the JAM frontend is opened with ext_* URL parameters (injected by the
Chrome extension), the jobs page should automatically open the add-job modal
with the supplied fields pre-filled, then clean the params from the URL.
"""

import time
import urllib.parse

from conftest import BaseTest


class TestExtensionAutoOpen(BaseTest):

    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    def _navigate_with_ext_params(self, **params) -> None:
        """Navigate to /jobs?ext_*=... while preserving the localStorage JWT."""

        qs = urllib.parse.urlencode(params)
        self.driver.get(f"{self.frontend_base_url}/jobs?{qs}")

    def test_salary_fields_are_prefilled(self) -> None:
        """Salary min/max are pre-filled from ext_salary_min / ext_salary_max."""

        self._navigate_with_ext_params(
            ext_title="Data Engineer",
            ext_salary_min="45000",
            ext_salary_max="65000",
            ext_deadline="2026-06-30",
        )
        modal = self.job_modal_utils.wait_for_edit_modal()
        assert "Data Engineer" in modal.text
        self.job_modal_utils.check_edit_modal(
            salary_min="45000",
            salary_max="65000",
            deadline="2026-06-30",
        )

    def test_url_params_cleaned_after_modal_opens(self) -> None:
        """ext_* params are stripped from the URL once the modal is triggered."""

        self._navigate_with_ext_params(
            ext_title="Platform Engineer",
            ext_salary_min="60000",
        )
        self.job_modal_utils.wait_for_edit_modal()
        time.sleep(0.5)

        assert "ext_title" not in self.driver.current_url
        assert "ext_salary_min" not in self.driver.current_url

    def test_no_modal_without_ext_title(self) -> None:
        """Without ext_title the modal must NOT auto-open (title is the required sentinel)."""

        self._navigate_with_ext_params(
            ext_company="Acme Corp",
            ext_salary_min="50000",
        )
        time.sleep(1)
        assert not self.job_modal_utils.wait_for_edit_modal_close()
