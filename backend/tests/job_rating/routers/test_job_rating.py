"""Tests for Job Raring routers."""

from app.job_rating import schemas
from tests.conftest import CRUDTestBase


class TestJobRatingCRUDAdminUser(CRUDTestBase):

    endpoint = "/job-ratings"
    out_schema = schemas.JobRatingOut
    test_data_ref = "test_job_ratings"
    actions_to_test = ["get_all"]
    admin_only = True
