"""Tests for the scraped jobs."""

from conftest import BaseTest


class TestBadge(BaseTest):

    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_jobs")
        self.login()
        self.job_table_utils.table_row_click(1)

    def test_view_badge_details(self) -> None:
        """Test viewing badge details from the job table."""

        badge = self.job_modal_utils.get_element("modal-view-job-CompanyBadge")
        self.context_menu(badge, "view")
        self.company_modal_utils.wait_for_view_modal()

    def test_view_edit_badge_details(self) -> None:
        """Test viewing badge details from the job table."""

        badge = self.job_modal_utils.get_element("modal-view-job-CompanyBadge")
        self.context_menu(badge, "view")
        self.company_modal_utils.wait_for_view_modal()
        self.company_modal_utils.edit_button("view").click()
        self.company_modal_utils.wait_for_edit_modal()
        self.company_modal_utils._fill_modal(name="New Company Name")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()
        updated_name = self.company_modal_utils.get_element("modal-view-job-CompanyBadge").text
        assert updated_name == "NEW COMPANY NAME"

    def test_edit_badge_details(self) -> None:
        """Test viewing badge details from the job table."""

        badge = self.job_modal_utils.get_element("modal-view-job-CompanyBadge")
        self.context_menu(badge, "edit")
        self.company_modal_utils.wait_for_edit_modal()
        self.company_modal_utils._fill_modal(name="New Company Name")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()
        updated_name = self.company_modal_utils.get_element("modal-view-job-CompanyBadge").text
        assert updated_name == "NEW COMPANY NAME"

    def test_delete(self) -> None:
        """Test viewing badge details from the job table."""

        badge = self.job_modal_utils.get_element("modal-view-job-CompanyBadge")
        self.context_menu(badge, "delete")
        self.delete_modal.confirm_button.click()
        self.assert_toast_message("Company deleted successfully.")
        modal = self.job_modal_utils.wait_for_view_modal()
        assert "Company\nNot Provided" in modal.text
