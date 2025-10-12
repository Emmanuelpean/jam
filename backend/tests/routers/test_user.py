"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

from app import schemas, models, utils
from tests.conftest import CRUDTestBase


class TestUsersCRUS(CRUDTestBase):
    endpoint = "/users"
    admin_only = True
    create_schema = schemas.UserCreate
    out_schema = schemas.UserOut
    test_data_ref = "test_users"
    create_data = [{"email": "test1@test.com", "password": "testpassword1"}]
    update_data = {"id": 1, "email": "newemail@test.com"}

    def test_update_admin_incorrect_email_format(self, admin_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff"}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_admin_existing_email(self, admin_client, admin_user, test_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": admin_user.email}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 400


class TestMe:

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""

        return session.query(models.User).filter(models.User.id == user_id).first()

    def test_get_current_user_profile_success(self, admin_client, admin_user, test_client, test_user) -> None:
        """Test successfully getting current user profile."""

        # Admin
        response = admin_client.get("/current_user")
        assert admin_user.email == response.json()["email"]

        # Non-admin
        response = test_client.get("/current_user")
        assert test_user.email == response.json()["email"]

    def test_update_email(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"email": "newemail@example.com", "current_password": test_user.password}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": test_user.password, "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200
        utils.verify_password(update_data["password"], self.get_user(test_user.id, session).password)

    def test_update_password_incorrect_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": "", "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 401

    def test_update_incorrect_email_format(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_user.password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 422

    def test_update_existing_email(self, session, test_client, test_user, admin_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": admin_user.email, "current_password": test_user.password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 400

    def test_update_settings(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).chase_threshold == 100

    def test_unauthorised_update(self, session, client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = client.put(f"/current_user", json=update_data)
        assert response.status_code == 401
