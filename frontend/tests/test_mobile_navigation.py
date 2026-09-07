"""Test the mobile navigation menu: opening/closing it from the page header, navigating between
pages, and landing on a data-table page that has no data yet."""

from frontend_base_test import BaseTest

MOBILE_WIDTH = 480
MOBILE_HEIGHT = 900

MENU_TOGGLE = "page-header-menu-toggle"
NAV_MENU = "mobile-nav-menu"


class TestMobileNavigation(BaseTest):
    """Test navigating the app through the mobile nav menu, starting from the dashboard."""

    page_url = "dashboard"
    user_fixture = "test_regular_user"

    def setup_function(self, request) -> None:
        """Shrink the browser to a mobile viewport before logging in, so the app starts in mobile mode."""

        self.driver.set_window_size(MOBILE_WIDTH, MOBILE_HEIGHT)
        self.login()

    # ------------------------------------------------------ HELPERS -----------------------------------------------

    def _menu_open(self) -> bool:
        """Whether the mobile nav menu is currently open."""

        return self.check_element_exists(NAV_MENU)

    def _open_menu(self) -> None:
        """Click the header's hamburger toggle to open the mobile nav menu."""

        self.get_element(MENU_TOGGLE).click()
        self.get_element(NAV_MENU)

    def _navigate_via_menu(self, nav_id: str, page: str) -> None:
        """Open the mobile nav menu, click the item with id ``nav_id``, and wait for ``page`` to load."""

        self._open_menu()
        self.get_element(nav_id).click()
        self.wait_for_page(page)

    # ------------------------------------------------------- TESTS ------------------------------------------------

    def test_menu_toggle_opens_and_closes(self) -> None:
        """The header's hamburger toggle opens the mobile nav menu, and toggling again closes it."""

        assert not self._menu_open()
        self._open_menu()
        assert self._menu_open()
        self.get_element(MENU_TOGGLE).click()
        assert not self._menu_open()

    def test_navigate_between_pages(self) -> None:
        """The mobile nav menu can be used to navigate from the dashboard to several other pages."""

        self._navigate_via_menu("nav-companies", "companies")
        assert not self._menu_open()

        self._navigate_via_menu("nav-contacts", "contacts")
        assert not self._menu_open()

        self._navigate_via_menu("nav-user-settings", "settings/account")
        assert not self._menu_open()

    def test_navigate_to_submenu_item(self) -> None:
        """A flattened submenu item (under the "Other" group) can be navigated to from the mobile menu."""

        self._navigate_via_menu("nav-tags", "keywords")
        assert not self._menu_open()

    def test_navigate_to_jobs_page_with_no_jobs_shows_empty_state(self) -> None:
        """Navigating to the Jobs page with no jobs yet shows the empty-state prompt, not the table."""

        self._navigate_via_menu("nav-jobs", "jobs")

        self.get_element("add-job-button")
        assert len(self.job_table_utils.table_rows) == 0

        # The empty state itself opens the "add" modal
        self.get_element("add-job-button").click()
        self.job_modal_utils.wait_for_edit_modal()
