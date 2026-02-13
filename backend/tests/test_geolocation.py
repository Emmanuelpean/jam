"""Tests for geolocation module."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from app.geolocation import call_geocoding_api, geocode_location
from app.models import Geolocation


class TestCallGeocodingApi:
    """Tests for call_geocoding_api function."""

    @patch("app.geolocation.requests.get")
    def test_returns_coordinates_and_address_on_success(self, mock_get) -> None:
        """Returns latitude, longitude, and address dict when API succeeds."""

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {
                    "city": "London",
                    "country": "United Kingdom",
                    "country_code": "gb",
                },
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        lat, lon, address = call_geocoding_api("London")

        assert lat == 51.5074456
        assert lon == -0.1277653
        assert address["city"] == "London"
        assert address["country"] == "United Kingdom"
        mock_get.assert_called_once()

    @patch("app.geolocation.requests.get")
    def test_returns_empty_address_dict_when_not_provided(self, mock_get) -> None:
        """Returns empty address dict when API result has no address field."""

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        lat, lon, address = call_geocoding_api("London")

        assert lat == 51.5074456
        assert lon == -0.1277653
        assert address == {}

    @patch("app.geolocation.requests.get")
    def test_raises_runtime_error_when_no_results(self, mock_get) -> None:
        """Raises RuntimeError when API returns empty results."""

        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("NonexistentPlace12345")

        assert "Nominatim API error" in str(exc_info.value)

    @patch("app.geolocation.requests.get")
    def test_raises_runtime_error_on_http_error(self, mock_get) -> None:
        """Raises RuntimeError when HTTP request fails."""

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("503 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)

    @patch("app.geolocation.requests.get")
    def test_raises_runtime_error_on_connection_error(self, mock_get) -> None:
        """Raises RuntimeError when connection fails."""

        mock_get.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)

    @patch("app.geolocation.requests.get")
    def test_raises_runtime_error_on_timeout(self, mock_get) -> None:
        """Raises RuntimeError when request times out."""

        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)

    @patch("app.geolocation.settings")
    @patch("app.geolocation.requests.get")
    def test_sends_correct_request_parameters(self, mock_get, mock_settings) -> None:
        """Sends correct query parameters and headers to API."""

        mock_settings.app_version = "1.0.0"
        mock_settings.main_email_username = "test@example.com"
        mock_response = MagicMock()
        mock_response.json.return_value = [{"lat": "51.5", "lon": "-0.1", "address": {}}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        call_geocoding_api("Cambridge, UK")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://nominatim.openstreetmap.org/search"
        assert call_args[1]["params"]["q"] == "Cambridge, UK"
        assert call_args[1]["params"]["format"] == "json"
        assert call_args[1]["params"]["limit"] == 1
        assert call_args[1]["params"]["addressdetails"] == 1
        assert call_args[1]["timeout"] == 5
        assert "User-Agent" in call_args[1]["headers"]

    @patch("app.geolocation.settings")
    @patch("app.geolocation.requests.get")
    def test_sends_structured_params_when_given_dict(self, mock_get, mock_settings) -> None:
        """Sends structured query parameters when given a dict instead of a string."""

        mock_settings.app_version = "1.0.0"
        mock_settings.main_email_username = "test@example.com"
        mock_response = MagicMock()
        mock_response.json.return_value = [{"lat": "51.5", "lon": "-0.1", "address": {}}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        call_geocoding_api({"city": "London", "country": "United Kingdom"})

        call_args = mock_get.call_args
        assert "q" not in call_args[1]["params"]
        assert call_args[1]["params"]["city"] == "London"
        assert call_args[1]["params"]["country"] == "United Kingdom"
        assert call_args[1]["params"]["format"] == "json"


class TestGeocodeLocation:
    """Tests for geocode_location function."""

    def test_returns_cached_geolocation_when_exists(self) -> None:
        """Returns cached geolocation without calling API if query exists."""

        mock_session = MagicMock()
        cached_geo = MagicMock(spec=Geolocation)
        cached_geo.id = 1
        cached_geo.query = "London"
        cached_geo.latitude = 51.5074456
        cached_geo.longitude = -0.1277653
        mock_session.query.return_value.filter_by.return_value.first.return_value = cached_geo

        result = geocode_location("London", mock_session)

        assert result == cached_geo
        mock_session.add.assert_not_called()

    @patch("app.geolocation.call_geocoding_api")
    @patch("app.geolocation.utils.open_json")
    def test_creates_new_geolocation_when_not_cached(self, mock_open_json, mock_api) -> None:
        """Calls API and creates new geolocation when query not in cache."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.return_value = (
            51.5074456,
            -0.1277653,
            {"city": "London", "country": "United Kingdom", "postcode": "SW1A 1AA"},
        )
        mock_open_json.return_value = [{"name": "United Kingdom"}]

        result = geocode_location("London", mock_session)

        mock_api.assert_called_once_with("London")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result is not None

    @patch("app.geolocation.call_geocoding_api")
    @patch("app.geolocation.utils.open_json")
    def test_matches_country_name_case_insensitive(self, mock_open_json, mock_api) -> None:
        """Matches country name in case-insensitive manner."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.return_value = (
            51.5074456,
            -0.1277653,
            {"city": "London", "country": "UNITED KINGDOM"},
        )
        mock_open_json.return_value = [{"name": "United Kingdom"}, {"name": "France"}]

        geocode_location("London", mock_session)

        # Check the geolocation was created with matched country name
        add_call = mock_session.add.call_args[0][0]
        assert add_call.country == "United Kingdom"

    @patch("app.geolocation.call_geocoding_api")
    def test_returns_none_on_api_failure(self, mock_api) -> None:
        """Returns None when API call fails."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.side_effect = RuntimeError("API error")

        result = geocode_location("NonexistentPlace", mock_session)

        assert result is None
        mock_session.add.assert_not_called()

    @patch("app.geolocation.call_geocoding_api")
    @patch("app.geolocation.utils.open_json")
    def test_handles_missing_address_fields(self, mock_open_json, mock_api) -> None:
        """Creates geolocation with None for missing address fields."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.return_value = (51.5074456, -0.1277653, {})
        mock_open_json.return_value = []

        geocode_location("Unknown Place", mock_session)

        add_call = mock_session.add.call_args[0][0]
        assert add_call.postcode is None
        assert add_call.city is None
        assert add_call.country is None

    @patch("app.geolocation.call_geocoding_api")
    @patch("app.geolocation.utils.open_json")
    def test_creates_geolocation_from_dict_query(self, mock_open_json, mock_api) -> None:
        """Creates geolocation with a stable cache key when given a dict query."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.return_value = (
            51.5074456,
            -0.1277653,
            {"city": "London", "country": "United Kingdom", "postcode": "SW1A 1AA"},
        )
        mock_open_json.return_value = [{"name": "United Kingdom"}]

        result = geocode_location({"city": "London", "country": "United Kingdom"}, mock_session)

        mock_api.assert_called_once_with({"city": "London", "country": "United Kingdom"})
        # Cache key should be sorted and formatted
        mock_session.query.return_value.filter_by.assert_called_with(query="city=London, country=United Kingdom")
        assert result is not None

    @patch("app.geolocation.call_geocoding_api")
    @patch("app.geolocation.utils.open_json")
    def test_does_not_match_unrecognized_country(self, mock_open_json, mock_api) -> None:
        """Sets country to None when country not in known countries list."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.return_value = (
            51.5074456,
            -0.1277653,
            {"city": "Test City", "country": "Unknown Country"},
        )
        mock_open_json.return_value = [{"name": "United Kingdom"}, {"name": "France"}]

        geocode_location("Test City", mock_session)

        add_call = mock_session.add.call_args[0][0]
        assert add_call.country is None


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
