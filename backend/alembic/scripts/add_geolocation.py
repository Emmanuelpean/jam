"""Script to add geolocation data to existing Location records."""

from app.models import Location
from app.database import get_db
from app.geolocation import geocode_location
from app.job_email_scraping.models import ScrapedJob


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


def add_geolocation_to_scraped_jobs() -> None:
    """Add geolocation data to existing ScrapedJob records in the database."""

    db = next(get_db())
    scraped_jobs = db.query(ScrapedJob).all()

    for scraped_job in scraped_jobs:
        if not scraped_job.geolocation:
            parts = [scraped_job.location_postcode, scraped_job.location_city, scraped_job.location_country]
            query = ", ".join(filter(None, parts))
            if query:
                geolocation = geocode_location(query, db)
                if geolocation:
                    scraped_job.geolocation_id = geolocation.id
    db.commit()
