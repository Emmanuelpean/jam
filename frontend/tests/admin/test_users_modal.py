"""Tests for the user management table (opened via the admin dashboard modal).

Reuses BaseTablePage for the standard table/CRUD coverage. The only user-specific
wrinkle is that `password` is an add-only field, so the three tests that fill the
shared `test_data` into an *edit* form are overridden to avoid it.
"""

from app import models
from helpers.table_page_utils import BaseTablePage


class TestUsersPage(BaseTablePage):
    """Test class for the admin Users table (opened via the admin dashboard modal)."""

    endpoint = "users"
    page_url = "admin"
    entry_type = "user"
    required_fields = ["email", "password"]
    test_data = {"email": "newuser@example.com", "password": "Password123!"}
    duplicate_fields = ["email"]
    model = models.User
    user_fixture = "test_admin_user"

    EDIT_EMAIL = "edited@example.com"

    def setup_function(self, request) -> None:
        super().setup_function(request)
        self.admin_page_utils.open_card("admin-card-users")

    def reload_page(self) -> None:
        """Reload the admin page and reopen the users modal so new entries appear."""

        self.refresh()
        self.admin_page_utils.open_card("admin-card-users")

    def create_entries(self, count: int = 1) -> list[models.User]:
        """Create user entries (distinct from the logged-in admin) for the CRUD tests."""

        return [self.create_user(self.db, email=f"user{i}@example.com", password="Password123!") for i in range(count)]

    # ----------------------------------------------------- ADD TEST ---------------------------------------------------

    def test_add_valid_entry(self) -> None:
        """Adding a user with an email and password creates it and lists it in the table.

        Overridden: the base test reopens the new entry in edit mode and checks the
        whole `test_data`, but `password` has no field in edit mode."""

        self.table_utils.set_page_item_select("100")
        n_entries = self.get_entries_count()
        initial_table_count = len(self.table_utils.table_rows)

        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(**self.test_data)  # email + password
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

        # The new user is in the database and the table
        assert self.get_entries_count() == n_entries + 1, "Expected user to be added to database"
        assert len(self.table_utils.table_rows) == initial_table_count + 1, "Expected user to be added to table"

        new_user = self.db.query(self.model).filter_by(email=self.test_data["email"]).first()
        assert new_user is not None, "Expected the new user in the database"

        # Reopen in view mode and confirm it shows the new user
        self.table_utils.table_row_click(new_user.id)
        self.modal_utils.test_view_modal(new_user)

    # ---------------------------------------------------- EDIT TEST ---------------------------------------------------

    def test_edit_entry_through_view_modal(self) -> None:
        """Editing a user's email via the view modal's edit button.

        Overridden to fill only the email (the edit form has no password field)."""

        user = self.load_entries()[0]
        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_row_click(user.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils._fill_modal(email=self.EDIT_EMAIL)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        self.modal_utils.cancel_button("view").click()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Editing a user's email via the right-click context menu.

        Overridden to fill only the email (the edit form has no password field)."""

        user = self.load_entries()[0]
        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_context_menu(user.id, "edit")
        self.modal_utils._fill_modal(email=self.EDIT_EMAIL)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"
