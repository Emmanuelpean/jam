"""Tests for the geolocation router (POST /geolocation/)."""

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


class TestGeolocationRouter(BaseTest):
    endpoint = "/geolocation/"

    def test_returns_cached_geolocation(self, session: Session, test_regular_user: FixtureUser) -> None:
        """POST with a query that already exists in the DB returns the cached result."""

        cached = self.create_geolocation(session, query="London", latitude=51.5074, longitude=-0.1278)
        response = test_regular_user.client.post(self.endpoint, json=cached.query)
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == cached.query
        assert float(data["latitude"]) == float(cached.latitude)
        assert float(data["longitude"]) == float(cached.longitude)

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        """POST without an auth token is rejected."""
        response = client.post(self.endpoint, json="London")
        assert response.status_code == 401
