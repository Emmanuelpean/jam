"""Utilities for the follow-up email modal."""

from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils
from helpers.select_utils import Select


class FollowUpEmailModalUtils(JamTestUtils):
    """Utilities for the Follow-Up Email Modal."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def wait_for_modal(self) -> WebElement:
        """Get the follow-up email modal element."""

        return self.get_element("follow-up-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the follow-up email modal to close."""

        self._wait_for_modal_close("follow-up-modal")

    @property
    def contact(self) -> Select:
        """Get the contact element in the modal."""

        return Select(self.get_element("contactId"))

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
