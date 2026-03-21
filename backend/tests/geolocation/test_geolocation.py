"""Tests for geolocation module."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import requests

import app.geolocation.geolocation as geolocation_module
from app.geolocation.geolocation import call_geocoding_api, geocode_location
from app.models import Geolocation
from tests.utils.create_data.utils import create_db_entries


class TestCallGeocodingApi:
    """Tests for call_geocoding_api function."""

    def test_returns_coordinates_and_address_on_success(self) -> None:
        """Returns latitude, longitude, and address dict when API succeeds."""

        result = call_geocoding_api("London")
        assert result[0] == 51.5074456
        assert result[1] == -0.1277653
        assert result[2] == {
            "ISO3166-2-lvl4": "GB-ENG",
            "city": "Greater London",
            "country": "United Kingdom",
            "country_code": "gb",
            "state": "England",
        }

    def test_raises_value_error_when_no_results(self) -> None:
        """Raises ValueError when API returns empty results."""

        # Default fixture response is already an empty list
        with pytest.raises(ValueError) as exc_info:
            call_geocoding_api("NonexistentPlace12345")

        assert "No results found" in str(exc_info.value)

    def test_raises_runtime_error_on_http_error(self, mock_nominatim_get) -> None:
        """Raises RuntimeError when HTTP request fails."""

        mock_nominatim_get.side_effect = requests.HTTPError("503 Server Error")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)


class TestGeocodeLocation:
    """Tests for geocode_location function."""

    def test_returns_cached_geolocation_when_exists(self, session, mock_nominatim_get) -> None:
        """Returns cached geolocation without calling API if query exists."""

        data = dict(query="London", latitude=51.5074456, longitude=-0.1277653)
        geo = create_db_entries(session, Geolocation, data)[0]
        result = geocode_location(geo.query, session)

        assert result.id == geo.id
        assert mock_nominatim_get.call_count == 0

    def test_creates_new_geolocation_when_not_cached(self, session) -> None:
        """Calls API and creates new geolocation when query not in cache."""

        result = geocode_location("London", session)

        assert result is not None
        assert result.latitude == 51.5074456
        assert result.longitude == -0.1277653

    def test_creates_geolocation_from_dict_query(self, session, mock_nominatim_get) -> None:
        """Creates geolocation with a stable sorted cache key when given a dict query."""

        result = geocode_location({"postcode": "10001", "city": "New York", "country": "United States"}, session)
        assert result is not None
        cached = session.query(Geolocation).filter_by(query="10001, New York, United States").first()
        assert cached is not None

    def test_decodes_html_entities_in_string_query(self, session, mock_nominatim_get) -> None:
        """Decodes HTML entities in string queries before calling the API."""

        geocode_location("London UK &amp;", session)
        assert mock_nominatim_get.call_args[1]["params"]["q"] == "London UK &"

    def test_decodes_html_entities_in_dict_query(self, session, mock_nominatim_get) -> None:
        """Decodes HTML entities in dict query values before calling the API."""

        geocode_location({"city": "Caf&eacute; City", "country": "UK"}, session)
        assert mock_nominatim_get.call_args[1]["params"]["q"] == "Café City, UK"

    def test_returns_empty_geolocation_when_no_results(self, session) -> None:
        """Returns an empty Geolocation record when the API finds no results, to avoid repeat API calls."""

        result = geocode_location("NonexistentPlace12345", session)
        assert result is not None
        assert result.query == "NonexistentPlace12345"
        assert result.latitude is None
        assert result.longitude is None

    def test_returns_none_on_api_failure(self, session, mock_nominatim_get) -> None:
        """Returns None when a network error occurs."""

        mock_nominatim_get.side_effect = requests.ConnectionError("Connection refused")
        result = geocode_location("SomePlace", session)
        assert result is None
        assert session.query(Geolocation).filter_by(query="SomePlace").first() is None

    def test_none_in_dict(self, session) -> None:
        """Check that the sanitation works even if None is in the dictionary"""

        result = geocode_location({"postcode": None, "city": "London", "country": None}, session)
        assert result is not None
        assert result.latitude is not None
        assert result.longitude is not None

    def test_all_none_in_dict(self, session) -> None:
        """Check that the sanitation works even if None is in the dictionary"""

        result = geocode_location({"postcode": None, "city": None, "country": None}, session)
        assert result is not None
        assert result.latitude is None
        assert result.longitude is None


class TestRateLimiting:
    """Tests for Nominatim API rate limiting."""

    @pytest.fixture(autouse=True)
    def mock_nominatim_get(self):
        """Override the global mock to keep real time.sleep for rate-limiting tests."""
        with patch("app.geolocation.geolocation.requests.get") as mock:
            mock.return_value = MagicMock()
            mock.return_value.raise_for_status = MagicMock()
            mock.return_value.json.return_value = []
            yield mock

    def test_concurrent_calls_are_spaced_at_least_1s_apart(self) -> None:
        """When multiple threads call the API simultaneously, calls are spaced >= 1s apart."""

        # Reset the last call time so the first call doesn't wait
        geolocation_module._last_call_time = 0.0

        call_times: list[float] = []
        lock = threading.Lock()

        original_get = geolocation_module.requests.get

        def tracking_get(*args, **kwargs):
            with lock:
                call_times.append(time.monotonic())
            return original_get(*args, **kwargs)

        geolocation_module.requests.get = tracking_get
        try:
            threads = [threading.Thread(target=call_geocoding_api, args=("London",)) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        finally:
            geolocation_module.requests.get = original_get

        call_times.sort()
        assert len(call_times) == 3
        for i in range(1, len(call_times)):
            gap = call_times[i] - call_times[i - 1]
            assert gap >= 0.9, f"Gap between call {i - 1} and {i} was only {gap:.3f}s"


class TestGeolocationCascade:
    """Tests for geolocation foreign key cascade behavior."""

    def test_deleting_location_does_not_delete_geolocation(self, session, test_locations, test_geolocations) -> None:
        """Deleting a location with a geolocation sets geolocation_id to NULL but does not delete the geolocation."""

        location = test_locations[0]
        geolocation_id = location.geolocation_id
        assert geolocation_id is not None

        session.delete(location)
        session.commit()

        # Geolocation should still exist
        geo = session.query(Geolocation).filter_by(id=geolocation_id).first()
        assert geo is not None

    def test_deleting_geolocation_sets_location_fk_to_null(self, session, test_locations, test_geolocations) -> None:
        """Deleting a geolocation sets the location's geolocation_id to NULL (ondelete=SET NULL)."""

        location = test_locations[0]
        geolocation_id = location.geolocation_id
        assert geolocation_id is not None

        geolocation = session.query(Geolocation).filter_by(id=geolocation_id).first()
        session.delete(geolocation)
        session.commit()

        session.refresh(location)
        assert location.geolocation_id is None
