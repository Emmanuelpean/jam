from app import schemas
from jose import jwt
from app.config import settings
import pytest


def test_create_user(client):
    user_data = {
        "username": "test",
        "email": "emmanuel.pean@gmail.com",
        "password": "pass123",
    }
    response = client.post("/users", json=user_data)
    new_user = schemas.UserOut(**response.json())  # validate the output
    for key in ("username", "email"):
        assert getattr(new_user, key) == user_data[key]
    assert response.status_code == 201


def test_login_user(test_user, client):
    user_data = {
        "username": test_user["email"],
        "password": test_user["password"],
    }
    response = client.post("/login", data=user_data)
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(
        login_response.access_token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    id: str = payload.get("user_id")
    assert id == test_user["id"]
    assert login_response.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "pass123", 403),
        ("emmanuel.pean@gmail.com", "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "pass123", 403),
        ("emmanuel.pean@gmail.com", None, 403),
    ],
)
def test_incorrect_login(email, password, status_code, client):
    response = client.post("/login/", data={"username": email, "password": password})

    assert response.status_code == status_code
