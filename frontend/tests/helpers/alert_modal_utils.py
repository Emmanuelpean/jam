"""Utilities for alert/confirm/delete/logout modals."""

from selenium.webdriver.remote.webelement import WebElement

from helpers.base_utils import BaseUtils


class AlertModalUtils(BaseUtils):
    """Utilities for the Confirm Modal."""

    key = ""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def wait_for_modal(self) -> WebElement:
        """Get the confirm modal element."""

        return self.get_element(f"{self.key}-alert-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the confirm modal to close."""

        self._wait_for_modal_close(f"{self.key}-alert-modal")

    @property
    def confirm_button(self) -> WebElement:
        """Get the confirm button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-confirm-button")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-cancel-button")


class ConfirmModalUtils(AlertModalUtils):
    """Utilities for the Confirm Modal."""

    key = "confirm"


class DeleteModalUtils(AlertModalUtils):
    """Utilities for the Delete Modal."""

    key = "delete"


class LogoutModalUtils(AlertModalUtils):
    """Utilities for the Logout Confirm Modal."""

    key = "logout"
