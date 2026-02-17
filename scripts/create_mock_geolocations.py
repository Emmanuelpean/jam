"""Geolocation handling using OpenStreetMap Nominatim API with caching."""

import time

import requests

from app.config import settings
from tests.utils.test_data.data_tables import LOCATION_DATA
from tests.utils.test_data import SCRAPED_JOB_DATA
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


data = {}
for location in LOCATION_DATA:
    query = [location.get("postcode"), location.get("city"), location.get("country")]
    query = ", ".join(filter(None, query))
    try:
        data[query] = call_geocoding_api(query).json()
        time.sleep(1)
    except Exception as e:
        data[query] = e

print(data)

data = {}
for scraped_job in SCRAPED_JOB_DATA:
    query = scraped_job.get("location")
    try:
        if query:
            data[query] = call_geocoding_api(query).json()
            time.sleep(1)
    except Exception as e:
        data[query] = e

print(data)


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
