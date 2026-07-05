"""Tests for Job Raring routers."""

import pytest

from app.job_rating import schemas
from tests.fixtures.users import FixtureUser
from tests.conftest import CRUDTestBase, make_undefined_method_params


class TestJobRatingCRUDAdminUser(CRUDTestBase):

    endpoint = "/job-ratings"
    out_schema = schemas.JobRatingOut
    test_data_ref = "test_job_ratings"
    actions_to_test = ["get_all"]
    admin_only = True


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
