"""Create real mock geolocations for testing using the Nominatim API."""

import requests

from app.config import settings
from tests.utils.test_data import SCRAPED_JOB_DATA, LOCATION_DATA
from tests.utils.test_data.geolocation import MOCK_GEOCODING_RESPONSES


def call_geocoding_api(query: str):
    """Geocode using OpenStreetMap Nominatim API directly.
    :param query: A location query string or a dict with structured params (postcode, city, country).
    :return: A tuple of (latitude, longitude, formatted_address).
    :raises RuntimeError: If the API call fails or returns no results."""

    print("Calling Nominatim API for query:", query)
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "limit": 1, "addressdetails": 1, "q": query}
    headers = {"User-Agent": f"JAM/{settings.app_version} ({settings.main_email_username})"}
    return requests.get(base_url, params=params, headers=headers, timeout=5)


def geocode_test_locations() -> None:
    """Run this to generate the mock geocoding responses for test locations"""

    data = {}
    for location in LOCATION_DATA:
        query = [location.get("postcode"), location.get("city"), location.get("country")]
        query = ", ".join(filter(None, query))
        data[query] = call_geocoding_api(query).json()

    print(data)


def geocode_test_scraped_jobs() -> None:
    """Run this to generate the mock geocoding responses for test scraped jobs"""

    data = {}
    for scraped_job in SCRAPED_JOB_DATA:
        query = scraped_job.get("location")
        if query:
            data[query] = call_geocoding_api(query).json()
    print(data)


def create_geolocation_entries_from_mock_api_results() -> None:
    """Once the mock geolocation data are saved in MOCK_GEOCODING_RESPONSES, run this to generate the test geolocation entries."""

    data = []
    for query, response in MOCK_GEOCODING_RESPONSES.items():
        if response:
            data.append(
                {
                    "query": query,
                    "latitude": response[0]["lat"],
                    "longitude": response[0]["lon"],
                    "data": response[0]["address"],
                }
            )
        else:
            data.append({"query": query})
    print(data)
