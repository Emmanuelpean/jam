"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

from fastapi import status

import utils
from app import schemas, models


class TestUser:

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""

        return session.query(models.User).filter(models.User.id == user_id).first()

    # ------------------------------------------------------- GET ------------------------------------------------------

    def test_get_all_users_admin(self, admin_client, test_users) -> None:
        """Test getting all users."""

        response = admin_client.get("/users")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(test_users)

    def test_get_all_users_non_admin(self, test_client) -> None:
        """Test getting all users."""

        response = test_client.get("/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_all_users_unauthorised(self, client) -> None:
        """Test getting all users."""

        response = client.get("/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ----------------------------------------------------- GET ID -----------------------------------------------------

    def test_get_user_by_id(self, admin_client, test_users) -> None:
        """Test successfully getting user by ID."""

        response = admin_client.get("/users/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_users[0].email

    def test_get_user_by_id_non_admin(self, test_client) -> None:
        """Test getting user by ID without admin privileges."""

        response = test_client.get("/users/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_by_id_unauthorised(self, client) -> None:
        """Test getting user by ID without authentication."""

        response = client.get("/users/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_by_id_not_found(self, admin_client, authorised_clients) -> None:
        """Test getting user by ID that does not exist."""

        response = admin_client.get(f"/users/{len(authorised_clients) + 1}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_create_user_authorised(self, test_client) -> None:
        """Test creating a new user."""

        user_data = {"email": "test_user@email.com", "password": "test_password"}
        response = test_client.post("/users", json=user_data)
        new_user = schemas.UserOut(**response.json())
        assert new_user.email == user_data["email"]
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_user_unauthorised(self, client) -> None:
        """Test creating a new user."""

        user_data = {"email": "test_user@email.com", "password": "test_password"}
        response = client.post("/users", json=user_data)
        new_user = schemas.UserOut(**response.json())
        assert new_user.email == user_data["email"]
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_user_limited(self, client, test_settings) -> None:
        """Test creating a new user when registration is limited."""

        user_data = {"email": "test_user1@email.com", "password": "test_password"}
        response = client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ------------------------------------------------------- PUT ------------------------------------------------------

    def test_update_admin(self, admin_client, admin_user, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": "newemail1@example.com"}
        response = admin_client.put(f"/users/{admin_user.id}", json=update_data)
        assert response.status_code == 200
        assert self.get_user(admin_user.id, session).email == update_data["email"]

    def test_update_admin_existing_email(self, admin_client, admin_user, test_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": admin_user.email}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 400

    def test_update_admin_incorrect_email_format(self, admin_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff"}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_non_admin(self, test_client, test_user, admin_user) -> None:
        """Test updating another user profile without admin privileges."""

        update_data = {"email": "newemail1@example.com", "current_password": admin_user.password}
        response = test_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 403

    def test_update_user_unauthorised(self, client) -> None:
        """Test updating user without authentication."""
        update_data = {"email": "newemail@example.com"}
        response = client.put("/users/0", json=update_data)
        assert response.status_code == 401

        response = client.put("/users/me", json=update_data)
        assert response.status_code == 401


class TestMe:

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""

        return session.query(models.User).filter(models.User.id == user_id).first()

    def test_get_current_user_profile_success(self, admin_client, admin_user, test_client, test_user) -> None:
        """Test successfully getting current user profile."""

        # Admin
        response = admin_client.get("/users/me")
        assert admin_user.email == response.json()["email"]

        # Non-admin
        response = test_client.get("/users/me")
        assert test_user.email == response.json()["email"]

    def test_update_email(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"email": "newemail@example.com", "current_password": test_user.password}
        response = test_client.put("/users/me", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": test_user.password, "password": "newpassword1"}
        response = test_client.put("/users/me", json=update_data)
        assert response.status_code == 200
        utils.verify_password(update_data["password"], self.get_user(test_user.id, session).password)

    def test_update_password_incorrect_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": "", "password": "newpassword1"}
        response = test_client.put("/users/me", json=update_data)
        assert response.status_code == 401

    def test_update_incorrect_email_format(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_user.password}
        response = test_client.put(f"/users/me", json=update_data)
        assert response.status_code == 422

    def test_update_existing_email(self, session, test_client, test_user, admin_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": admin_user.email, "current_password": test_user.password}
        response = test_client.put(f"/users/me", json=update_data)
        assert response.status_code == 400

    def test_update_settings(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = test_client.put(f"/users/me", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).chase_threshold == 100

    def test_unauthorised_update(self, session, client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = client.put(f"/users/me", json=update_data)
        assert response.status_code == 401
