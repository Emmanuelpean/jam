"""Client fixtures for API testing."""

from typing import Any, Generator

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import database, models
from app.core.oauth2 import create_access_token
from app.main import app


@pytest.fixture
def client(session: Session) -> Generator[TestClient, Any, None]:
    """Fixture that provides a test client with an overridden database dependency."""

    def override_get_db() -> Generator[Session, Any, None]:
        """Return the test session for database operations."""
        yield session

    app.dependency_overrides[database.get_db] = override_get_db  # noqa
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)


@pytest.fixture
def authorised_client_factory(client: TestClient):
    """Return a factory that builds an authenticated client for an arbitrary user."""

    def _make(user: models.User) -> TestClient:
        token = create_access_token({"user_id": user.id}, token_version=user.token_version)
        authorised_client = TestClient(client.app)
        authorised_client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
        return authorised_client

    return _make
