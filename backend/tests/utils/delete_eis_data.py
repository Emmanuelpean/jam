"""Utility script to delete all EIS-related data from the database for testing purposes."""

from app.eis import models
from app.database import get_db

# noinspection PyUnusedImports
from app.job_rating.models import JobRating

# noinspection PyUnusedImports
from app.models import UserQualification

db = next(get_db())
db.query(models.ScrapedJob).delete()
db.query(models.JobAlertEmail).delete()
db.query(models.EisServiceLog).delete()
db.query(models.EisServiceError).delete()
db.commit()
