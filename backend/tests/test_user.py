"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

import pytest
from fastapi import status
from jose import jwt

from app import schemas, models
from app.config import settings


class TestUser:

    # ------------------------------------------------------- GET ------------------------------------------------------

    def test_get_all_users_admin(self, authorised_clients, test_users) -> None:
        """Test getting all users."""

        response = authorised_clients[0].get("/users")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(test_users)

    def test_get_all_users_non_admin(self, authorised_clients, test_users) -> None:
        """Test getting all users."""

        response = authorised_clients[1].get("/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_all_users_unauthorised(self, client, test_users) -> None:
        """Test getting all users."""

        response = client.get("/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ----------------------------------------------------- GET ME -----------------------------------------------------

    def test_get_current_user_profile_success(self, authorised_clients, test_users) -> None:
        """Test successfully getting current user profile."""

        # Admin
        response = authorised_clients[0].get("/users/me")
        assert test_users[0].email == response.json()["email"]

        # Non-admin
        response = authorised_clients[1].get("/users/me")
        assert test_users[1].email == response.json()["email"]

    # ----------------------------------------------------- GET ID -----------------------------------------------------

    def test_get_user_by_id(self, authorised_clients, test_users) -> None:
        """Test successfully getting user by ID."""

        response = authorised_clients[0].get("/users/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_users[0].email

    def test_get_user_by_id_non_admin(self, authorised_clients, test_users) -> None:
        """Test getting user by ID without admin privileges."""

        response = authorised_clients[1].get("/users/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_by_id_unauthorised(self, client, test_users) -> None:
        """Test getting user by ID without authentication."""

        response = client.get("/users/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_by_id_not_found(self, authorised_clients) -> None:
        """Test getting user by ID that does not exist."""

        response = authorised_clients[0].get(f"/users/{len(authorised_clients) + 1}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --------------------------------------------------- PUT (ADMIN) --------------------------------------------------

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""

        return session.query(models.User).filter(models.User.id == user_id).first()

    def test_update_same_user_admin(self, authorised_clients, test_users, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": "newemail@example.com"}
        test_user = test_users[0]
        response = authorised_clients[0].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_different_user_admin(self, authorised_clients, test_users, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": "newemail1@example.com"}
        test_user = test_users[1]
        response = authorised_clients[0].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_me_user_admin(self, authorised_clients, test_users, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": "newemail2@example.com"}
        test_user = test_users[0]
        response = authorised_clients[0].put(f"/users/me", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_different_user_admin_existing(self, authorised_clients, test_users, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": test_users[1].email}
        response = authorised_clients[0].put(f"/users/{test_users[0].id}", json=update_data)
        assert response.status_code == 400

    def test_update_different_user_admin_incorrect(self, authorised_clients, test_users, session) -> None:
        """Test successfully updating a different user profile.
        The user password is not needed"""

        update_data = {"email": "ff"}
        response = authorised_clients[0].put(f"/users/{test_users[0].id}", json=update_data)
        assert response.status_code == 422

    # ------------------------------------------------- PUT (NON ADMIN) ------------------------------------------------

    def test_update_same_user_non_admin(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": "newemail@example.com", "current_password": test_user.password}
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_different_user_non_admin(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": "newemail1@example.com", "current_password": test_user.password}
        test_user = test_users[0]
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 403

    def test_update_me_user_non_admin(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": "newemail@example.com", "current_password": test_user.password}
        response = authorised_clients[1].put(f"/users/me", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email == update_data["email"]

    def test_update_nopassword_user_non_admin(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": "newemail@example.com"}
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 401

    def test_update_different_user_non_admin_existing(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": test_users[0].email, "current_password": test_user.password}
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 400

    def test_update_different_user_non_admin_incorrect(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"email": "ff", "current_password": test_user.password}
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_user_noemail(self, authorised_clients, test_users, session) -> None:
        """Test updating a different user profile without admin privileges.
        Require password"""

        test_user = test_users[1]
        update_data = {"current_password": test_user.password, "new_password": "newpassword1"}
        response = authorised_clients[1].put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 200

    # ----------------------------------------------- PUT (UNAUTHORISED) -----------------------------------------------

    def test_update_user_unauthorised(self, client) -> None:
        """Test updating current user profile without authentication."""

        update_data = {"email": "newemail@example.com"}
        response = client.put(f"/users/0", json=update_data)
        assert response.status_code == 401

        update_data = {"email": "newemail@example.com"}
        response = client.put(f"/users/me", json=update_data)
        assert response.status_code == 401

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_create_user(self, client) -> None:
        """Test creating a new user."""

        user_data = {
            "email": "test_user@email.com",
            "password": "test_password",
        }
        response = client.post("/users", json=user_data)
        new_user = schemas.UserOut(**response.json())
        assert new_user.email == user_data["email"]
        assert response.status_code == status.HTTP_201_CREATED


class TestLogin:

    def test_login_user(self, test_users, client) -> None:
        """Test successful login for an existing user."""

        user_data = {
            "username": test_users[0].email,
            "password": test_users[0].password,
        }
        response = client.post("/login", data=user_data)
        login_response = schemas.Token(**response.json())
        payload = jwt.decode(
            login_response.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("user_id")
        assert user_id == test_users[0].id
        assert login_response.token_type == "bearer"
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "email, password, status_code",
        [
            ("wrongemail@gmail.com", "pass123", 403),
            ("user1@email.com", "wrongpassword", 403),
            ("wrongemail@gmail.com", "wrongpassword", 403),
            (None, "pass123", 403),
            ("user1@email.com", None, 403),
        ],
    )
    def test_incorrect_login(self, email, password, status_code, client) -> None:
        """Test login failure scenarios with incorrect or incomplete credentials."""

        response = client.post("/login/", data={"username": email, "password": password})
        assert response.status_code == status_code
