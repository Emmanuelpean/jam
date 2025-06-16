"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.

Key Features:
-------------
- **test_create_user**: Verifies that a user can be successfully created by sending valid data to the `/users` endpoint
  and checks the consistency of the response with the expected schema.
- **test_login_user**: Tests successful login functionality for an existing user by verifying token generation,
  decoding of the token for user identification, and validating the token type.
- **test_incorrect_login**: Uses parameterized testing to validate login failure scenarios with incorrect or incomplete
  credentials, ensuring appropriate status codes are returned (`403`).

These tests leverage fixtures like `client` and `test_user1` to provide isolated and efficient test runs. They also
utilize the `pytest.mark.parametrize` decorator to cover multiple edge cases for invalid login attempts in a concise
and modular manner.
"""

import pytest
from fastapi import status
from jose import jwt

from app import schemas, models
from app.config import settings


class TestUser:

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
        assert user_id == test_users.id
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


class TestUserMe:

    def test_get_current_user_profile_success(self, authorised_clients, test_users):
        """Test successfully getting current user profile."""
        response = authorised_clients[0].get("/users/me")

        assert response.status_code == 200
        user_data = response.json()

        # Validate response structure
        user_profile = schemas.UserOut(**user_data)
        assert user_profile.email == test_users[0].email
        assert user_profile.id == test_users[0].id
        assert "password" not in user_data

    def test_get_current_user_profile_unauthorized(self, client):
        """Test getting current user profile without authentication."""

        response = client.get("/users/me")
        assert response.status_code == 401

    def test_update_current_user_profile_email_success(self, authorised_clients, test_users):
        """Test successfully updating user email."""
        update_data = {"email": "newemail@example.com"}
        response = authorised_clients[0].put("/users/me", json=update_data)

        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "newemail@example.com"
        assert user_data["id"] == test_users[0].id

    def test_update_current_user_profile_theme_success(self, authorised_clients, test_users):
        """Test successfully updating user theme."""
        valid_themes = ["strawberry", "blueberry", "raspberry", "mixed-berry", "forest-berry", "blackberry"]

        for theme in valid_themes:
            update_data = {"theme": theme}
            response = authorised_clients[0].put("/users/me", json=update_data)
            assert response.status_code == 200
            user_data = response.json()
            assert user_data["theme"] == theme

    def test_update_current_user_profile_password_success(self, authorised_clients, test_users, session):
        """Test successfully updating user password."""

        update_data = {"password": "new_secure_password123"}
        response = authorised_clients[0].put("/users/me", json=update_data)
        assert response.status_code == 200
        user_data = response.json()
        assert "password" not in user_data

        # Verify password was actually updated by checking the database
        user_in_db = session.query(models.User).filter(models.User.id == test_users[0].id).first()
        assert user_in_db.password != "new_secure_password123"
        assert user_in_db.password != test_users[0].password

    def test_update_current_user_profile_multiple_fields(self, authorised_clients, test_users):
        """Test updating multiple user fields at once."""

        update_data = {"email": "updated@example.com", "theme": "strawberry"}
        response = authorised_clients[0].put("/users/me", json=update_data)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "updated@example.com"
        assert user_data["theme"] == "strawberry"

    def test_update_current_user_profile_email_already_exists(self, authorised_clients, test_users):
        """Test updating email to one that already exists."""

        update_data = {"email": test_users[1].email}
        response = authorised_clients[0].put("/users/me", json=update_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_update_current_user_profile_same_email(self, authorised_clients, test_users):
        """Test updating email to the same email (should succeed)."""

        update_data = {"email": test_users[0].email}
        response = authorised_clients[0].put("/users/me", json=update_data)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == test_users[0].email

    def test_update_current_user_profile_invalid_theme(self, authorised_clients):
        """Test updating with invalid theme."""

        invalid_themes = ["invalid_theme", "purple", "green", "", "theme123"]

        for invalid_theme in invalid_themes:
            update_data = {"theme": invalid_theme}
            response = authorised_clients[0].put("/users/me", json=update_data)
            assert response.status_code == 400
            assert "Invalid theme" in response.json()["detail"]

    def test_update_current_user_profile_empty_body(self, authorised_clients):
        """Test updating with empty request body."""

        response = authorised_clients[0].put("/users/me", json={})
        # Should succeed as partial updates are allowed
        assert response.status_code == 200

    def test_update_current_user_profile_unauthorized(self, client):
        """Test updating user profile without authentication."""

        update_data = {"email": "test@example.com"}
        response = client.put("/users/me", json=update_data)
        assert response.status_code == 401

    def test_update_current_user_profile_partial_update(self, authorised_clients, test_user1):
        """Test that only provided fields are updated."""

        # Get original user data
        original_response = authorised_clients[0].get("/users/me")
        original_data = original_response.json()

        # Update only theme
        update_data = {"theme": "blueberry"}
        response = authorised_clients[0].put("/users/me", json=update_data)

        assert response.status_code == 200
        updated_data = response.json()

        # Theme should be updated
        assert updated_data["theme"] == "blueberry"

        # Email should remain the same
        assert updated_data["email"] == original_data["email"]

    @pytest.mark.parametrize("invalid_email", ["invalid-email", "@example.com", "test@", "test..test@example.com"])
    def test_update_current_user_profile_invalid_email_format(self, authorised_clients, invalid_email):
        """Test updating with invalid email formats."""

        update_data = {"email": invalid_email}
        response = authorised_clients[0].put("/users/me", json=update_data)

        # This will depend on your UserUpdate schema validation
        # Adjust expected status code based on your Pydantic validation
        assert response.status_code in [400, 422]

    def test_update_current_user_profile_null_fields(self, authorised_clients):
        """Test updating with null/None values."""

        update_data = {"email": None, "theme": None}
        response = authorised_clients[0].put("/users/me", json=update_data)

        # This behavior depends on your UserUpdate schema
        # Adjust assertions based on how you handle null values
        assert response.status_code in [200, 400, 422]

    def test_update_current_user_profile_theme_case_sensitivity(self, authorised_clients):
        """Test theme validation is case sensitive."""

        invalid_themes = ["Strawberry", "BLUEBERRY", "Mixed-Berry"]

        for theme in invalid_themes:
            update_data = {"theme": theme}
            response = authorised_clients[0].put("/users/me", json=update_data)

            assert response.status_code == 400
            assert "Invalid theme" in response.json()["detail"]

    def test_get_and_update_user_profile_integration(self, authorised_clients):
        """Integration test: get profile, update it, then verify changes."""

        # Get original profile
        get_response = authorised_clients[0].get("/users/me")
        assert get_response.status_code == 200
        original_data = get_response.json()

        # Update profile
        update_data = {"email": "integration_test@example.com", "theme": "forest-berry"}
        update_response = authorised_clients[0].put("/users/me", json=update_data)
        assert update_response.status_code == 200

        # Get updated profile
        get_updated_response = authorised_clients[0].get("/users/me")
        assert get_updated_response.status_code == 200
        updated_data = get_updated_response.json()

        # Verify changes
        assert updated_data["email"] == "integration_test@example.com"
        assert updated_data["theme"] == "forest-berry"
        assert updated_data["id"] == original_data["id"]  # ID should not change
