"""Routers for Job Rating related endpoints."""

from app import models
from app.job_rating import schemas
from app.routers.utility import generate_data_table_crud_router


job_rating_router = generate_data_table_crud_router(
    table_model=models.JobRating,
    out_schema=schemas.JobRatingOut,
    endpoint="job-ratings",
    not_found_msg="Job Rating not found",
    allowed_actions=["get_all"],
    admin_only=True,
)
