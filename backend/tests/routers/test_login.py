import pytest
from jose import jwt

from app import schemas
from app.config import settings


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
