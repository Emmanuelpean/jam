"""Utility script to delete all EIS-related data from the database for testing purposes."""

from app import model_registry
from app.database import get_db


# noinspection PyUnusedImports
from app.models import UserQualification

db = next(get_db())
db.query(model_registry.ScrapedJob).delete()
db.query(model_registry.JobAlertEmail).delete()
db.query(model_registry.EisServiceLog).delete()
db.query(model_registry.EisServiceError).delete()
db.query(model_registry.JobRating).delete()
db.query(model_registry.JobRatingServiceLog).delete()
db.commit()
