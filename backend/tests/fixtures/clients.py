"""Client fixtures for API testing."""

from typing import Any, Generator

import pytest
from sqlalchemy import orm
from starlette.testclient import TestClient

from app import database
from app.core.oauth2 import create_access_token
from app.main import app
from tests.utils import test_data as td


@pytest.fixture
def tokens(test_users) -> list[str]:
    """Fixture that generates access tokens for the given test users."""
    return [create_access_token({"user_id": user.id}) for user in test_users]


@pytest.fixture
def client(session) -> Generator[TestClient, Any, None]:
    """Fixture that provides a test client with an overridden database dependency."""

    def override_get_db() -> Generator[orm.Session, Any, None]:
        yield session

    app.dependency_overrides[database.get_db] = override_get_db  # noqa
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)


@pytest.fixture
def authorised_clients(client: TestClient, tokens: list[str]) -> list[TestClient]:
    """Fixture that provides a list of authenticated test clients."""
    clients = []
    for token in tokens:
        authorised_client = TestClient(client.app)
        authorised_client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
        clients.append(authorised_client)
    return clients


@pytest.fixture
def admin_client(authorised_clients) -> TestClient:
    """Fixture for an admin client."""
    return authorised_clients[td.ADMIN_USER_INDEX]


@pytest.fixture
def regular_user_client(authorised_clients) -> TestClient:
    """Fixture for a non-admin client."""
    return authorised_clients[td.REGULAR_USER_INDEX]


@pytest.fixture
def demo_user_client(authorised_clients) -> TestClient:
    """Fixture for a demo user client"""
    return authorised_clients[td.DEMO_USER_INDEX]
