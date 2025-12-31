"""Tests for the scraped jobs."""

from selenium.webdriver.remote.webelement import WebElement

from conftest import BaseTest, models, BaseUtilsClass
from react_select import ReactSelect


class TestFollowUpEmail(BaseTest):

    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_jobs")
        self.followup_modal = FollowUpEmailModalUtils(self.driver, self.frontend_base_url, self.db)
        self.confirm_modal = ConfirmModalUtils(self.driver, self.frontend_base_url, self.db)
        self.login()

    def test_generate_followup_email(self) -> None:
        """Test generating a follow-up email and displaying a toast notification."""

        self.job_table_utils.table_context_menu(1, "followup")
        modal = self.followup_modal.wait_for_modal()
        expected = (
            "Follow Up Email Generator\n"
            "Contact\n"
            "John Doe\n"
            "Email Subject\n"
            "Email Body\n"
            "Hi John,\n"
            "\n"
            "I hope you are well. I am writing to follow up on my application for the "
            "Senior Python Developer position and to kindly ask if there have been any "
            "updates regarding the recruitment process.\n"
            "\n"
            "Thank you for your time and consideration.\n"
            "\n"
            "Best regards,\n"
            "\n"
            "Regular User\n"
            "Close\n"
            "Send Email"
        )
        assert modal.text == expected
        self.followup_modal.contact.open_menu()
        self.followup_modal.contact.select_by_visible_text("Alex Johnson")
        assert "Alex" in self.followup_modal.body.text

    def test_cancel(self) -> None:
        """Test cancelling the follow-up email modal."""

        self.job_table_utils.table_context_menu(1, "followup")
        self.followup_modal.wait_for_modal()
        self.followup_modal.cancel_button.click()
        self.followup_modal.wait_for_modal_close()

    def test_send_email(self) -> None:
        """Test sending the follow-up email and displaying a toast notification."""

        self.job_table_utils.table_context_menu(1, "followup")
        self.followup_modal.wait_for_modal()
        self.followup_modal.send_button.click()
        self.confirm_modal.wait_for_modal()
        self.confirm_modal.confirm_button.click()
        self.assert_toast_message("Follow up email update created successfully.")
        entry = self.db.query(models.JobApplicationUpdate).order_by(models.JobApplicationUpdate.id.desc()).first()
        assert entry.note.startswith("Follow up email sent to John Doe")
        self.followup_modal.wait_for_modal_close()

    def test_send_email_no_update(self) -> None:
        """Test sending the follow-up email and displaying a toast notification."""

        self.job_table_utils.table_context_menu(1, "followup")
        self.followup_modal.wait_for_modal()
        self.followup_modal.send_button.click()
        self.confirm_modal.wait_for_modal()
        self.confirm_modal.cancel_button.click()
        self.followup_modal.wait_for_modal_close()

    def test_send_email_gmail(self) -> None:
        """Test sending the follow-up email via Gmail and displaying a toast notification."""

        self.job_table_utils.table_context_menu(1, "followup")
        self.followup_modal.wait_for_modal()
        self.followup_modal.send_menu_button.click()
        self.followup_modal.gmail_option.click()
        self.wait_for_windows(2)
        self.switch_to_window(-1)
        assert "mail.google.com" in self.driver.current_url
        self.followup_modal.wait_for_modal_close()

    def test_send_email_outlook(self) -> None:
        """Test sending the follow-up email via Outlook and displaying a toast notification."""

        self.job_table_utils.table_context_menu(1, "followup")
        self.followup_modal.wait_for_modal()
        self.followup_modal.send_menu_button.click()
        self.followup_modal.outlook_option.click()
        self.wait_for_windows(2)
        self.switch_to_window(-1)
        assert "outlook.office.com" in self.driver.current_url
        self.followup_modal.wait_for_modal_close()

    def test_contact_send_email(self) -> None:
        """Test sending the follow-up email from the job view modal."""

        self.job_table_utils.table_row_click(1)
        self.job_modal_utils.wait_for_view_modal()
        person_badge = self.get_element("modal-view-job-person-0")
        self.context_menu(person_badge, "followup")
        self.followup_modal.wait_for_modal()
        assert self.followup_modal.contact_text == "John Doe"
        assert "John" in self.followup_modal.body.text
        self.followup_modal.cancel_button.click()
        self.followup_modal.wait_for_modal_close()
        person_badge = self.get_element("modal-view-job-person-1")
        self.context_menu(person_badge, "followup")
        self.followup_modal.wait_for_modal()
        assert self.followup_modal.contact_text == "Mike Taylor"
        assert "Mike" in self.followup_modal.body.text


class FollowUpEmailModalUtils(BaseUtilsClass):
    """Utilities for the Follow-Up Email Modal."""

    def wait_for_modal(self) -> WebElement:
        """Get the follow-up email modal element."""

        return self.get_element("follow-up-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the follow-up email modal to close."""

        self._wait_for_modal_close("follow-up-modal")

    @property
    def contact(self) -> ReactSelect:
        """Get the contact element in the modal."""

        return ReactSelect(self.get_element("contactId"))

    @property
    def contact_text(self) -> str:
        """Get the contact text element in the modal."""

        return self.get_element("contactId").text

    @property
    def subject(self) -> WebElement:
        """Get the subject element in the modal."""

        return self.get_element("subject")

    @property
    def body(self) -> WebElement:
        """Get the body element in the modal."""

        return self.get_element("body")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element("cancel-btn")

    @property
    def send_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("send-btn")

    @property
    def send_menu_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("dropdown-split-email")

    @property
    def gmail_option(self) -> WebElement:
        """Get the Gmail option in the send menu."""

        return self.get_element("gmail-btn")

    @property
    def outlook_option(self) -> WebElement:
        """Get the Outlook option in the send menu."""

        return self.get_element("outlook-btn")

    @property
    def default_option(self) -> WebElement:
        """Get the Yahoo option in the send menu."""

        return self.get_element("default-email-btn")


class ConfirmModalUtils(BaseUtilsClass):
    """Utilities for the Confirm Modal."""

    def wait_for_modal(self) -> WebElement:
        """Get the confirm modal element."""

        return self.get_element("confirm-alert-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the confirm modal to close."""

        self._wait_for_modal_close("confirm-alert-modal")

    @property
    def confirm_button(self) -> WebElement:
        """Get the confirm button in the modal."""

        return self.get_element("confirm-alert-modal-confirm-button")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element("confirm-alert-modal-cancel-button")
