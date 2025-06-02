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
from jose import jwt

from app import schemas
from app.config import settings


def test_create_user(client) -> None:
    """Test creating a new user."""

    user_data = {
        "email": "test_user@email.com",
        "password": "test_password",
    }
    response = client.post("/users", json=user_data)
    new_user = schemas.UserOut(**response.json())  # validate the output
    assert new_user.email == user_data["email"]
    assert response.status_code == 201


def test_login_user(test_user1, client) -> None:
    """Test successful login for an existing user."""

    user_data = {
        "username": test_user1["email"],
        "password": test_user1["password"],
    }
    response = client.post("/login", data=user_data)
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(
        login_response.access_token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    user_id = payload.get("user_id")
    assert user_id == test_user1["id"]
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
def test_incorrect_login(email, password, status_code, client) -> None:
    """Test login failure scenarios with incorrect or incomplete credentials."""

    response = client.post("/login/", data={"username": email, "password": password})
    assert response.status_code == status_code
