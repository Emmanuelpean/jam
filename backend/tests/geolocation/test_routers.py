"""Tests for the geolocation router (POST /geolocation/)."""


class TestGeolocationRouter:
    endpoint = "/geolocation/"

    def test_returns_cached_geolocation(self, test_geolocations, test_regular_user) -> None:
        """POST with a query that already exists in the DB returns the cached result."""

        cached = test_geolocations[0]
        response = test_regular_user.client.post(self.endpoint, json=cached.query)
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == cached.query
        assert float(data["latitude"]) == float(cached.latitude)
        assert float(data["longitude"]) == float(cached.longitude)

    def test_unauthenticated_returns_401(self, client) -> None:
        """POST without an auth token is rejected."""
        response = client.post(self.endpoint, json="London")
        assert response.status_code == 401
