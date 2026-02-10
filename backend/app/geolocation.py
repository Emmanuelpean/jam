"""Geolocation handling using OpenStreetMap Nominatim API with caching."""

import traceback

import requests
from sqlalchemy.orm import Session

from app import utils
from app.config import settings
from app.models import Geolocation


def call_geocoding_api(query: str) -> tuple[float, float, dict]:
    """Geocode using OpenStreetMap Nominatim API directly.
    :param query: The location query string.
    :return: A tuple of (latitude, longitude, formatted_address).
    :raises RuntimeError: If the API call fails or returns no results."""

    print("Calling Nominatim API for query:", query)
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1, "addressdetails": 1}

    headers = {"User-Agent": f"JAM/{settings.app_version} ({settings.main_email_username})"}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            result = data[0]
            return float(result["lat"]), float(result["lon"]), result.get("address", {})
        else:
            raise ValueError(f"No results found for: {query}")

    except Exception as e:
        raise RuntimeError(f"Nominatim API error: {str(e)}")


def geocode_location(query_string: str, session: Session) -> Geolocation | None:
    """Geocode a location or scraped job using cached results when available.
    Links the location/scraped job to a Geolocation record via foreign key.
    :param query_string: The location query string.
    :param session: SQLAlchemy session for database operations.
    :return: The geolocation ID if successful, else None."""

    # Check cache first
    cached = session.query(Geolocation).filter_by(query=query_string).first()

    if cached:
        return cached
    else:
        try:
            lat, lon, address_dict = call_geocoding_api(query_string)

            # Create new geolocation entry
            countries = utils.open_json("app/data/countries.json")
            oms_country = address_dict.get("country")
            matched_country = None
            if oms_country:
                for country in countries:
                    if oms_country.lower() == country["name"].lower():
                        matched_country = country["name"]
                        break

            # noinspection PyArgumentList
            new_geo = Geolocation(
                query=query_string,
                latitude=lat,
                longitude=lon,
                postcode=address_dict.get("postcode"),
                city=address_dict.get("city"),
                country=matched_country,
                county=address_dict.get("county"),
                state=address_dict.get("state"),
                suburb=address_dict.get("suburb"),
            )
            session.add(new_geo)
            session.commit()
            session.refresh(new_geo)
            return new_geo

        # If no result was found, store the query string to avoid repeated calls to the API
        except ValueError:
            # noinspection PyArgumentList
            new_geo = Geolocation(query=query_string)
            session.add(new_geo)
            session.commit()
            session.refresh(new_geo)

        except Exception as e:
            print(f"Warning: Could not geocode '{query_string}': {e}")
            print(traceback.format_exc())
            return None
