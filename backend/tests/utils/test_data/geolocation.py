"""Mock fixtures for geocoding API calls.

The canned responses live in the app package (``app.geolocation.mock_responses``) because
``call_geocoding_api`` serves them directly when ``settings.test_mode`` is set, so no test ever
reaches the live Nominatim API. Re-exported here for backwards-compatible test imports.
"""

from app.geolocation.mock_responses import MOCK_GEOCODING_RESPONSES

__all__ = ["MOCK_GEOCODING_RESPONSES"]
