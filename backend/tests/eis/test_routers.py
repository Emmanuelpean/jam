from app.eis import schemas
from tests.conftest import CRUDTestBase
from tests.utils.table_data import JOB_ALERT_EMAIL_DATA, JOB_SCRAPED_DATA


class TestJobAlertEmailCRUD(CRUDTestBase):
    endpoint = "/jobalertemails"
    schema = schemas.JobAlertEmailCreate
    out_schema = schemas.JobAlertEmailOut
    test_data = "test_job_alert_emails"
    create_data = JOB_ALERT_EMAIL_DATA
    update_data = {
        "id": 1,
        "subject": "Updated Python",
    }
    add_fixture = ["test_service_logs"]


class TestScrapedJobCRUD(CRUDTestBase):
    endpoint = "/scrapedjobs"
    schema = schemas.ScrapedJobCreate
    out_schema = schemas.ScrapedJobOut
    test_data = "test_scraped_jobs"
    create_data = JOB_SCRAPED_DATA
    update_data = {
        "id": 1,
        "title": "Updated Python",
    }
