"""Tests for EIS routers."""

from starlette import status

from app.eis import schemas
from tests.conftest import CRUDTestBase
from tests.utils.table_data import JOB_ALERT_EMAIL_DATA


class TestJobAlertEmailCRUD(CRUDTestBase):
    endpoint = "/job_alert_emails"
    create_schema = schemas.JobAlertEmailCreate
    out_schema = schemas.JobAlertEmailOut
    test_data_ref = "test_job_alert_emails"
    create_data = JOB_ALERT_EMAIL_DATA
    update_data = {
        "id": 1,
        "subject": "Updated Python",
    }
    required_fixture = ["test_service_logs"]
    actions_to_test = ["get"]


class TestScrapedJobCRUD(CRUDTestBase):

    endpoint = "/scraped_jobs"
    create_schema = schemas.ScrapedJobCreate
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    update_data = {
        "id": 1,
        "is_imported": True,
    }
    actions_to_test = ["put"]

    def test_get_all(
        self,
        test_users,
        authorised_clients,
        test_scraped_jobs,
    ) -> None:
        """Test retrieving all scraped jobs for the authorized user that are scraped, not imported, active"""

        test_data = self.get_user_data(test_users, test_scraped_jobs)
        client = self._get_admin_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "?page=1&page_size=20&search=Test")
        assert response.status_code == status.HTTP_200_OK
        # jobs = []
        # for job in test_data:
        #     if job.is_scraped and not job.is_imported and job.owner_id == 1 and job.is_active:
        #         jobs.append(job)
        # assert len(response.json()) == len(jobs)
        # # self.check_output(jobs, response.json())
