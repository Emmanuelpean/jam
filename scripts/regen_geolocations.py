"""Script to delete and generate geolocations for all the scraped jobs and locations"""

from app.database import session_local
from app.geolocation.geolocation import geocode_location
from app.models import ScrapedJob, Geolocation, Location
from app.job_email_scraping.location_parser import parse_location


def run():
    session = session_local()
    try:
        # Null out FK references before deleting geolocations
        session.query(Location).update({Location.geolocation_id: None})
        session.query(ScrapedJob).update({ScrapedJob.geolocation_id: None})

        # Delete all geolocations
        session.query(Geolocation).delete()
        session.commit()

        # Add geolocation to Locations
        locations = session.query(Location).all()
        for location in locations:
            query = {"postcode": location.postcode, "city": location.city, "country": location.country}
            geolocation = geocode_location(query, session)
            if geolocation:
                location.geolocation_id = geolocation.id
                session.commit()

        # Add geolocation to ScrapedJobs
        scraped_jobs = session.query(ScrapedJob).all()
        for scraped_job in scraped_jobs:
            if scraped_job.location:
                parsed_location, parsed_attendance = parse_location(scraped_job.location)
                scraped_job.parsed_location = parsed_location
                if parsed_location:
                    geolocation = geocode_location(parsed_location, session)
                    if geolocation:
                        scraped_job.geolocation_id = geolocation.id
                        scraped_job.location_postcode = geolocation.postcode
                        scraped_job.location_city = geolocation.city
                        scraped_job.location_country = geolocation.country
                        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    run()
