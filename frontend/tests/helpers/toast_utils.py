"""Utilities for the toast notification shown after user actions."""

from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class ToastUtils(JamTestUtils):
    """Test class for the toast notification."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    @property
    def toast(self) -> WebElement:
        """Get the toast element."""

        return self.get_element("toast")

    def assert_toast_message(self, error_message: str) -> None:
        """Assert that the given message is displayed on the toast, then dismiss it."""

        element = self.toast
        assert error_message in element.text, f"Message not found: {error_message} in {element.text}"
        element.click()  # Dismiss toast
