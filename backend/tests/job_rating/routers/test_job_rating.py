"""Tests for Job Raring routers."""

import pytest
from sqlalchemy.orm import Session

from app import models
from app.job_rating import schemas
from tests.fixtures.users import FixtureUser
from tests.conftest import CRUDTestBase, make_undefined_method_params


class TestJobRatingCRUDAdminUser(CRUDTestBase[models.JobRating]):

    endpoint = "/job-ratings"
    out_schema = schemas.JobRatingOut
    actions_to_test = ["get_all"]
    admin_only = True

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.JobRating:
        return self.create_job_rating(session, owner, **overrides)


class TestJobRatingUndefinedMethods:
    ENDPOINT = "job-ratings"
    DEFINED_ACTIONS = ["GET_ALL"]
    UNDEFINED_ACTIONS = ["PUT", "POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(
        self,
        http_method,
        path_suffix,
        expected_status,
        test_admin_user: FixtureUser,
    ):
        response = test_admin_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
