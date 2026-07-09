"""Utilities for the admin dashboard's cards and the modal they open into."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class AdminPageUtils(JamTestUtils):
    """Test class for the admin dashboard (/admin): its cards and the shared page modal.

    Page-specific util classes for cards that open into a dashboard modal (e.g.
    ServiceDashboardUtils, UsagePageUtils) extend this to reuse `open_card`/`admin_page_modal`."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    @property
    def admin_page_modal(self) -> WebElement:
        """The large modal an admin card opens into."""

        return self.get_element("admin-page-modal", enabled=False)

    def open_card(self, card_id: str) -> None:
        """Open an admin dashboard card's modal by clicking its title.
        Clicks the card title (not the card itself) to avoid the sparkline hover overlay some cards show."""

        card = self.get_element(card_id, enabled=False)
        self.get_element("card-title", By.CLASS_NAME, parent=card).click()
        assert self.admin_page_modal
