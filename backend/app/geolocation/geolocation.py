"""Geolocation handling using OpenStreetMap Nominatim API with caching."""

import html
import logging
import threading
import time
import traceback

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Geolocation

_last_call_time = 0.0
_api_lock = threading.Lock()


def call_geocoding_api(query: str) -> tuple[float, float, dict]:
    """Geocode using OpenStreetMap Nominatim API directly.
    :param query: A location query string or a dict with structured params (postcode, city, country).
    :return: A tuple of (latitude, longitude, formatted_address).
    :raises RuntimeError: If the API call fails or returns no results."""

    global _last_call_time

    print("Calling Nominatim API for query:", query)
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "limit": 1, "addressdetails": 1, "q": query, "accept-language": "en"}
    headers = {"User-Agent": f"JAM/{settings.app_version} ({settings.main_email_username})"}

    try:
        with _api_lock:
            elapsed = time.monotonic() - _last_call_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            _last_call_time = time.monotonic()
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"Nominatim API error: {str(e)}")

    if data and len(data) > 0:
        result = data[0]
        return float(result["lat"]), float(result["lon"]), result.get("address", {})
    else:
        raise ValueError(f"No results found for: {query}")


def geocode_location(
        query: str,
        db: Session,
        logger: logging.Logger | None = None,
) -> Geolocation | None:
    """Geocode a location or scraped job using cached results when available.
    Links the location/scraped job to a Geolocation record via foreign key.
    :param query: A location query string or a dict with structured params (postcode, city, country).
    :param db: SQLAlchemy session for database operations.
    :param logger: AppLogger instance
    :return: The geolocation ID if successful, else None."""

    # Decode HTML entities and normalise whitespace
    sanitised_query = html.unescape(query).strip()

    # Check cache first
    cached = db.query(Geolocation).filter_by(query=sanitised_query).first()

    if cached:
        return cached
    else:
        try:
            lat, lon, address_dict = call_geocoding_api(sanitised_query)

            new_geo = Geolocation(
                query=sanitised_query,
                latitude=lat,
                longitude=lon,
                data=address_dict,
                postcode=address_dict.get("postcode"),
                city=address_dict.get("town") or address_dict.get("city") or address_dict.get("province"),
                country=address_dict.get("country"),
            )
            db.add(new_geo)
            db.commit()
            db.refresh(new_geo)
            message = f"Successfully geocode '{sanitised_query}' to '{new_geo.id}'"
            if logger is not None:
                logger.info(message)
            else:
                print(message)
            return new_geo

        # If no result was found, store the query string to avoid repeated calls to the API
        except ValueError:
            new_geo = Geolocation(query=sanitised_query)
            db.add(new_geo)
            db.commit()
            db.refresh(new_geo)
            message = f"Failed to geocode '{sanitised_query}'. Stored in '{new_geo.id}'"
            if logger is not None:
                logger.warning(message)
            else:
                print(message)
            return new_geo

        except Exception as e:
            print(f"Warning: Could not geocode '{sanitised_query}': {e}")
            print(traceback.format_exc())
            message = f"Failed to geocode '{sanitised_query}' due to error {e}"
            if logger is not None:
                logger.warning(message)
            else:
                print(message)
            return None
