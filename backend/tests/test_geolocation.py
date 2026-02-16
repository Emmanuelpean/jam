"""Tests for geolocation module."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from app.geolocation import call_geocoding_api, geocode_location
from app.models import Geolocation
from tests.utils.create_data.utils import create_db_entries


class TestCallGeocodingApi:
    """Tests for call_geocoding_api function."""

    def test_returns_coordinates_and_address_on_success(self, mock_nominatim_get) -> None:
        """Returns latitude, longitude, and address dict when API succeeds."""

        mock_nominatim_get.return_value.json.return_value = [
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

        lat, lon, address = call_geocoding_api("London")

        assert lat == 51.5074456
        assert lon == -0.1277653
        assert address["city"] == "London"
        assert address["country"] == "United Kingdom"
        mock_nominatim_get.assert_called_once()

    def test_returns_empty_address_dict_when_not_provided(self, mock_nominatim_get) -> None:
        """Returns empty address dict when API result has no address field."""

        mock_nominatim_get.return_value.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
            }
        ]

        lat, lon, address = call_geocoding_api("London")

        assert lat == 51.5074456
        assert lon == -0.1277653
        assert address == {}

    def test_raises_value_error_when_no_results(self, mock_nominatim_get) -> None:
        """Raises ValueError when API returns empty results."""

        # Default fixture response is already an empty list
        with pytest.raises(ValueError) as exc_info:
            call_geocoding_api("NonexistentPlace12345")

        assert "No results found" in str(exc_info.value)

    def test_raises_runtime_error_on_http_error(self, mock_nominatim_get) -> None:
        """Raises RuntimeError when HTTP request fails."""

        mock_nominatim_get.return_value.raise_for_status.side_effect = requests.HTTPError("503 Server Error")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)

    def test_raises_runtime_error_on_connection_error(self, mock_nominatim_get) -> None:
        """Raises RuntimeError when connection fails."""

        mock_nominatim_get.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)

    def test_raises_runtime_error_on_timeout(self, mock_nominatim_get) -> None:
        """Raises RuntimeError when request times out."""

        mock_nominatim_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(RuntimeError) as exc_info:
            call_geocoding_api("London")

        assert "Nominatim API error" in str(exc_info.value)


class TestGeocodeLocation:
    """Tests for geocode_location function."""

    def test_returns_cached_geolocation_when_exists(self, session) -> None:
        """Returns cached geolocation without calling API if query exists."""

        data = dict(query="London", latitude=51.5074456, longitude=-0.1277653, city="London")
        geo = create_db_entries(session, Geolocation, data)[0]

        result = geocode_location(geo.query, session)

        assert result.id == geo.id

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
    def test_decodes_html_entities_in_string_query(self, mock_api) -> None:
        """Decodes HTML entities in string queries before geocoding."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.side_effect = ValueError("No results found")

        geocode_location("London UK &amp;", mock_session)

        mock_api.assert_called_once_with("London UK &")

    @patch("app.geolocation.call_geocoding_api")
    def test_decodes_html_entities_in_dict_query(self, mock_api) -> None:
        """Decodes HTML entities in dict query values before geocoding."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.side_effect = ValueError("No results found")

        geocode_location({"city": "Caf&eacute; City", "country": "UK"}, mock_session)

        mock_api.assert_called_once_with({"city": "Café City", "country": "UK"})

    @patch("app.geolocation.call_geocoding_api")
    def test_caches_empty_result_when_no_geocoding_results(self, mock_api) -> None:
        """Caches an empty Geolocation record when API finds no results, to avoid repeat calls."""

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_api.side_effect = ValueError("No results found for: NonexistentPlace")

        geocode_location("NonexistentPlace", mock_session)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        add_call = mock_session.add.call_args[0][0]
        assert add_call.query == "NonexistentPlace"
        assert add_call.latitude is None

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
