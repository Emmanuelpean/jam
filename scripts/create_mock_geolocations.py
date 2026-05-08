"""Create real mock geolocations for testing using the Nominatim API."""

import time

import requests

from app.config import settings
from app.resources import COUNTRIES
from tests.utils.test_data import JOB_DATA, SCRAPED_JOB_DATA
from tests.utils.test_data.geolocation import MOCK_GEOCODING_RESPONSES


def call_geocoding_api(query: str):
    """Geocode using OpenStreetMap Nominatim API directly.
    :param query: A location query string or a dict with structured params (postcode, city, country).
    :return: A tuple of (latitude, longitude, formatted_address).
    :raises RuntimeError: If the API call fails or returns no results."""

    print("Calling Nominatim API for query:", query)
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "limit": 1, "addressdetails": 1, "q": query, "accept-language": "en"}
    headers = {"User-Agent": f"JAM/1.4 ({settings.main_email_username})"}
    return requests.get(base_url, params=params, headers=headers, timeout=5)


def geocode_test_jobs() -> None:
    """Run this to generate the mock geocoding responses for test locations. Then copy the results to MOCK_GEOCODING_RESPONSES in test_data/geolocation.py"""

    data = {}
    for job in JOB_DATA + SCRAPED_JOB_DATA:
        time.sleep(1)
        query = job.get("location")
        if query:
            data[query] = call_geocoding_api(query).json()
    print(data)


def create_geolocation_entries_from_mock_api_results() -> None:
    """Once the mock geolocation data are saved in MOCK_GEOCODING_RESPONSES, run this to generate the test geolocation entries."""

    data = []
    for query, response in MOCK_GEOCODING_RESPONSES.items():
        if response:
            address = response[0]["address"]
            oms_country = address.get("country")
            matched_country = None
            if oms_country:
                for country in COUNTRIES:
                    if oms_country.lower() == country["name"].lower():
                        matched_country = country["name"]
                        break

            data.append(
                {
                    "query": query,
                    "latitude": response[0]["lat"],
                    "longitude": response[0]["lon"],
                    "data": response[0]["address"],
                    "country": matched_country,
                    "postcode": address.get("postcode"),
                    "city": address.get("town") or address.get("city") or address.get("province"),
                }
            )
        else:
            data.append({"query": query})
    print(data)
