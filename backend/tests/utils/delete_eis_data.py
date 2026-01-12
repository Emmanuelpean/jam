"""Utility script to delete all EIS-related data from the database for testing purposes."""

from app.database import get_db


# noinspection PyUnusedImports
from data_tables.models import UserQualification

db = next(get_db())
db.query(model_registry.ScrapedJob).delete()
db.query(model_registry.JobEmail).delete()
db.query(model_registry.JobEmailScrapingServiceLog).delete()
db.query(model_registry.JobEmailScrapingServiceError).delete()
db.query(model_registry.JobRating).delete()
db.query(model_registry.JobRatingServiceLog).delete()
db.commit()
