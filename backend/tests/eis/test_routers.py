from app.eis import schemas
from conftest import CRUDTestBase
from tests.utils.table_data import SERVICE_LOG_DATA, JOB_ALERT_EMAIL_DATA, JOB_SCRAPED_DATA


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


class TestServiceLogCRUD(CRUDTestBase):
    endpoint = "/servicelogs"
    schema = schemas.EisServiceLogCreate
    out_schema = schemas.EisServiceLogOut
    test_data = "test_service_logs"
    create_data = SERVICE_LOG_DATA
    update_data = {
        "id": 1,
        "name": "Updated Python",
    }
