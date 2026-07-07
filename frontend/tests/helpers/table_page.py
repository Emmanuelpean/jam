import datetime as dt
import time

import pytest
from selenium.webdriver.common.by import By

from frontend_base_test import BaseTest
from helpers.formatting import contiguous_subdicts


class BaseTablePage(BaseTest):
    """Base class for testing data-table pages.

    Subclasses declare the page/endpoint metadata and implement ``create_entries`` to build the
    rows a test needs. Test data is created per test rather than shared through a fixture: each
    test calls ``create_entries`` (via ``load_entries``) for the rows it needs, then reloads the
    page so they appear in the table."""

    user_fixture = "test_regular_user"
    table_utils = None
    modal_utils = None

    # Parameters needed
    entry_type = ""  # entry type, used to resolve the correct *_table_utils / *_modal_utils helpers
    endpoint = ""  # endpoint of the table, used to query the data
    test_data = {}  # test data used to fill the modal (adding entries, adding incorrect entries, editing entries)
    required_fields = []  # required fields for adding entries. if empty, assume that any field is required
    duplicate_fields = []  # fields which are required to be unique
    columns = []  # table column keys user for search and sorting
    sorting_columns = []  # columns which can be sorted, if empty assume all columns can be sorted
    model = None  # database model class for the entry type

    def setup_function(self, request) -> None:
        """Resolve the table/modal helpers for this entry type and log in."""

        self.table_utils = getattr(self, f"{self.entry_type}_table_utils")
        self.modal_utils = getattr(self, f"{self.entry_type}_modal_utils")
        self.login()

    # -------------------------------------------------- DATA CREATION -------------------------------------------------

    def create_entries(self, count: int = 1) -> list:
        """Create ``count`` entries (and any FK dependencies) owned by ``self.user`` and return them.

        Must be implemented by subclasses."""

        raise NotImplementedError

    def reload_page(self) -> None:
        """Reload the page so newly created entries appear in the table.

        Overridden by pages that show the table inside a modal (a plain refresh would close it).
        """

        self.refresh()

    def load_entries(self, count: int = 1) -> list:
        """Create ``count`` entries and reload the page so they appear in the table."""

        entries = self.create_entries(count)
        self.reload_page()
        self.table_utils.wait_for_table_load()
        return entries

    def get_entries_count(self) -> int:
        """Get the number of entries in the database (scoped to the logged-in user for owned models)."""

        query = self.db.query(self.model)
        if hasattr(self.model, "owner_id"):
            query = query.filter_by(owner_id=self.user.id)
        return query.count()

    # ------------------------------------------------------ TABLE -----------------------------------------------------

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly across the default and increased page sizes"""

        self.load_entries(25)
        n_entries = self.get_entries_count()

        # Default 20 entries display
        assert len(self.table_utils.table_rows) == min([20, n_entries])

        # Increase to 40
        self.table_utils.set_page_item_select("40")
        self.table_utils.wait_for_table_load()
        assert len(self.table_utils.table_rows) == min([40, n_entries])

    @staticmethod
    def get_search_value(value, key: str) -> str:
        """Get the search value for a given column key"""

        if key == "companyBadge":
            return value.company.name
        elif key == "jobBadge":
            return value.job.title + " (" + value.job.company.name + ")"
        result = getattr(value, key)
        if isinstance(result, str):
            return result
        elif isinstance(result, dt.datetime):
            return result.strftime("%d/%m/%Y")
        else:
            return ""

    # --------------------------------------------------- VIEW TESTS ---------------------------------------------------

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        entry = self.load_entries()[0]
        self.table_utils.set_page_item_select("100")
        self.table_utils.table_row_click(entry.id)
        self.modal_utils.test_view_modal(entry)

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        entry = self.load_entries()[0]
        self.table_utils.table_context_menu(entry.id, "view")
        self.modal_utils.test_view_modal(entry)

    # --------------------------------------------------- DELETE TEST --------------------------------------------------

    def test_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        entry = self.load_entries()[0]
        self.table_utils.table_context_menu(entry.id, "delete")
        self.modal_utils.wait_for_delete_modal()
        self.delete_modal.confirm_button.click()
        self.delete_modal.wait_for_modal_close()
        time.sleep(0.1)
        self.table_utils.wait_for_disappear(f"table-row-{entry.id}")

        # Check that the entry was deleted from the database
        db_data = self.db.query(self.model).filter_by(id=entry.id).first()
        assert db_data is None, "Expected entry to be deleted from database"

    def test_view_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        entry = self.load_entries()[0]
        self.table_utils.table_row_click(entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils.delete_button("edit").click()
        self.modal_utils.wait_for_delete_modal()
        self.delete_modal.confirm_button.click()
        self.delete_modal.wait_for_modal_close()
        time.sleep(0.1)
        self.table_utils.wait_for_disappear(f"table-row-{entry.id}")

        # Check that the entry was deleted from the database
        db_data = self.db.query(self.model).filter_by(id=entry.id).first()
        assert db_data is None, "Expected entry to be deleted from database"

    # ----------------------------------------------------- ADD TEST ---------------------------------------------------

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry"""

        self.load_entries()
        self.table_utils.set_page_item_select("100")

        # Determine the number of entries in the db and in the table
        n_entries = self.get_entries_count()
        initial_table_count = len(self.table_utils.table_rows)

        # Add the new entry
        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

        # Check that the new entry was properly added to the db and table
        n_entries_new = self.get_entries_count()
        assert n_entries_new == n_entries + 1, "Expected entry to be added to database"
        new_table_count = len(self.table_utils.table_rows)
        assert new_table_count == initial_table_count + 1, "Expected entry to be added to table"

        entries = self.db.query(self.model).all()
        entry_id = max([entry.id for entry in entries])
        entry = [entry for entry in entries if entry.id == entry_id][0]

        # Reopen the modal in view mode and check contents
        self.table_utils.table_row_click(entry_id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.test_view_modal(entry)

        # Reopen in edit mode and check contents
        self.table_utils.table_context_menu(entry_id, "edit")
        self.modal_utils.check_edit_modal(**self.test_data)

    def test_add_duplicate_entry(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        if not self.duplicate_fields:
            pytest.skip("Duplicate entries are allowed")

        self.load_entries()

        # Add the new entry
        self.table_utils.add_entity_button.click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

        # Try to add the same entry again
        self.table_utils.add_entity_button.click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils._fill_modal(duplicate_fields=self.duplicate_fields, **self.test_data)
        self.modal_utils.assert_confirm_button_disabled("edit")
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

    def test_add_incomplete_entry(self) -> None:
        """Test that adding a new entry without all required information shows an error"""

        self.load_entries()

        if len(self.required_fields) > 1:
            dictionaries = contiguous_subdicts({key: self.test_data[key] for key in self.required_fields})
        else:
            dictionaries = [dict()]

        for d in dictionaries:
            self.table_utils.add_entity_button.click()
            self.modal_utils._fill_modal(**d)
            self.modal_utils.confirm_button("edit").click()
            self.modal_utils.get_element(".invalid-feedback", By.CSS_SELECTOR)
            self.modal_utils.cancel_button("edit").click()
            self.modal_utils.wait_for_edit_modal_close()

    def test_add_entry_cancel(self) -> None:
        """Test cancelling a new entry creation."""

        self.table_utils.add_entity_button.click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

    # ---------------------------------------------------- EDIT TEST ---------------------------------------------------

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        entry = self.load_entries()[0]
        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_row_click(entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        self.modal_utils.cancel_button("view").click()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        entry = self.load_entries()[0]
        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_context_menu(entry.id, "edit")
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_cancel_edit_view(self) -> None:
        """Test cancelling an entry edit opened via the view modal"""

        entry = self.load_entries()[0]
        self.table_utils.table_row_click(entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        self.modal_utils.wait_for_view_modal()

    def test_cancel_edit(self) -> None:
        """Test cancelling an entry edit opened via the edit modal"""

        entry = self.load_entries()[0]
        self.table_utils.table_context_menu(entry.id, "edit")
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
