"""Script to add geolocation data to existing Location records."""

from app.database import get_db
from app.geolocation import geocode_location
from app.model_registry import Location


def add_geolocation_to_locations() -> None:
    """Add geolocation data to existing Location records in the database."""

    db = next(get_db())
    locations = db.query(Location).all()

    for location in locations:
        if not location.geolocation:
            parts = [location.postcode, location.city, location.country]
            query = ", ".join(filter(None, parts))
            geolocation = geocode_location(query, db)
            if geolocation:
                location.geolocation_id = geolocation.id
    db.commit()
