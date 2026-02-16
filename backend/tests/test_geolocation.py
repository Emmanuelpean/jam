"""Tests for geolocation module."""

import pytest
import requests

from app.geolocation import call_geocoding_api, geocode_location
from app.models import Geolocation
from tests.utils.create_data.utils import create_db_entries


class TestCallGeocodingApi:
    """Tests for call_geocoding_api function."""

    def test_returns_coordinates_and_address_on_success(self, mock_nominatim_get) -> None:
        """Returns latitude, longitude, and address dict when API succeeds."""

        mock_nominatim_get.side_effect = None
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

        mock_nominatim_get.side_effect = None
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

        mock_nominatim_get.side_effect = None
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

    def test_creates_new_geolocation_when_not_cached(self, session, mock_nominatim_get) -> None:
        """Calls API and creates new geolocation when query not in cache."""

        mock_nominatim_get.side_effect = None
        mock_nominatim_get.return_value.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {
                    "city": "London",
                    "country": "United Kingdom",
                    "postcode": "SW1A 1AA",
                },
            },
        ]

        result = geocode_location("London", session)

        assert result is not None
        assert result.latitude == 51.5074456
        assert result.longitude == -0.1277653
        assert result.city == "London"
        assert result.postcode == "SW1A 1AA"

    def test_matches_country_name_case_insensitive(self, session, mock_nominatim_get) -> None:
        """Matches country name case-insensitively against the known countries list."""

        mock_nominatim_get.side_effect = None
        mock_nominatim_get.return_value.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {
                    "city": "London",
                    "country": "UNITED KINGDOM",
                },
            },
        ]

        result = geocode_location("London", session)

        assert result.country == "United Kingdom"

    def test_decodes_html_entities_in_string_query(self, session, mock_nominatim_get) -> None:
        """Decodes HTML entities in string queries before calling the API."""

        geocode_location("London UK &amp;", session)

        assert mock_nominatim_get.call_args[1]["params"]["q"] == "London UK &"

    def test_decodes_html_entities_in_dict_query(self, session, mock_nominatim_get) -> None:
        """Decodes HTML entities in dict query values before calling the API."""

        geocode_location({"city": "Caf&eacute; City", "country": "UK"}, session)

        assert mock_nominatim_get.call_args[1]["params"]["city"] == "Café City"

    def test_returns_empty_geolocation_when_no_results(self, session) -> None:
        """Returns an empty Geolocation record when the API finds no results, to avoid repeat API calls."""

        # mock_nominatim_get (autouse) returns [] by default, causing call_geocoding_api to raise ValueError
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

    def test_handles_missing_address_fields(self, session, mock_nominatim_get) -> None:
        """Creates geolocation with None for missing address fields."""

        mock_nominatim_get.side_effect = None
        mock_nominatim_get.return_value.json.return_value = [
            {"lat": "51.5074456", "lon": "-0.1277653", "address": {}},
        ]

        result = geocode_location("Unknown Place", session)

        assert result.postcode is None
        assert result.city is None
        assert result.country is None

    def test_creates_geolocation_from_dict_query(self, session, mock_nominatim_get) -> None:
        """Creates geolocation with a stable sorted cache key when given a dict query."""

        mock_nominatim_get.side_effect = None
        mock_nominatim_get.return_value.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {"city": "London", "country": "United Kingdom", "postcode": "SW1A 1AA"},
            },
        ]

        result = geocode_location({"city": "London", "country": "United Kingdom"}, session)

        assert result is not None
        cached = session.query(Geolocation).filter_by(query="city=London, country=United Kingdom").first()
        assert cached is not None

    def test_does_not_match_unrecognized_country(self, session, mock_nominatim_get) -> None:
        """Sets country to None when the API returns a country not in the known countries list."""

        mock_nominatim_get.side_effect = None
        mock_nominatim_get.return_value.json.return_value = [
            {
                "lat": "51.5074456",
                "lon": "-0.1277653",
                "address": {"city": "Test City", "country": "Zanzibar Moonbase Alpha"},
            },
        ]

        result = geocode_location("Test City", session)

        assert result.country is None


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
