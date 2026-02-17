"""Script to delete and generate geolocations for all the scraped jobs and locations"""

from app.database import session_local
from app.models import ScrapedJob, Geolocation


def run():
    session = session_local()
    try:
        # Replace the geolocation city with town or city
        geolocations = session.query(Geolocation).all()
        for geolocation in geolocations:
            if geolocation.data:
                new = geolocation.data.get("town") or geolocation.data.get("city")
                geolocation.city = new
                session.commit()

        # Update the scraped jobs
        scraped_jobs = session.query(ScrapedJob).all()
        for scraped_job in scraped_jobs:
            if scraped_job.geolocation:
                scraped_job.location_city = scraped_job.geolocation.city
                session.commit()

    finally:
        session.close()


if __name__ == "__main__":
    run()
