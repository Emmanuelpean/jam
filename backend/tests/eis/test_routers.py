"""Tests for EIS routers."""

from starlette import status

from app.eis import schemas
from tests.conftest import CRUDTestBase
from tests.utils.table_data import JOB_ALERT_EMAIL_DATA


class TestJobAlertEmailCRUD(CRUDTestBase):
    endpoint = "/job_alert_emails"
    create_schema = schemas.JobAlertEmailCreate
    out_schema = schemas.JobAlertEmailOut
    test_data = "test_job_alert_emails"
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
    test_data = "test_scraped_jobs"
    update_data = {
        "id": 1,
        "is_imported": True,
    }
    actions_to_test = ["get", "put"]

    def test_get_all_success(self, test_scraped_jobs, authorised_clients) -> None:
        """Test retrieving all scraped jobs for the authorized user that are scraped, not imported, active"""

        client = self._get_authorized_client(authorised_clients)
        response = self.get_all(client)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_scraped_jobs, response.json())
        jobs = []
        for job in test_scraped_jobs:
            if job.is_scraped and not job.is_imported and job.owner_id == 1 and job.is_active:
                jobs.append(job)
        assert len(response.json()) == len(jobs)
