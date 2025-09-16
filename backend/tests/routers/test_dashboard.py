"""
Test module for API router endpoints covering CRUD operations for JAM entities.

This module contains comprehensive test classes for the dashboard endpoint"""

import datetime
from tests.utils.table_data import DATE_FORMAT


class TestDashboardRouter:
    """Test class for the dashboard router endpoints"""

    def test_success(self, authorised_clients, test_jobs, test_interviews, test_job_application_updates) -> None:
        """Test get_all_updates endpoint returns unified updates"""

        response = authorised_clients[0].get("/dashboard")
        assert response.status_code == 200

        data = response.json()
        statistics, needs_chase, all_updates, upcoming_interviews, upcoming_deadlines = (
            data["statistics"], data["needs_chase"], data["all_updates"], data["upcoming_interviews"], data["upcoming_deadlines"])
        assert statistics == {"jobs": 17, "job_applications": 13, "job_application_pending": 11, "interviews": 12}
        assert len(needs_chase) == 5
        assert len(all_updates) == 10
        assert len(upcoming_interviews) == 5
        assert len(upcoming_deadlines) == 1

        # Update a job
        job_id = needs_chase[0]["id"]
        update_json = {"date": datetime.datetime.now().strftime(DATE_FORMAT), "type": "received", "job_id": job_id}
        response = authorised_clients[0].post("jobapplicationupdates", json=update_json)
        assert response.status_code == 201
        needs_chase = authorised_clients[0].get("/dashboard").json()["needs_chase"]
        assert len(needs_chase) == 4

    def test_unauthorized(self, client) -> None:
        """Test that unauthorised requests are rejected"""

        response = client.get("/dashboard")
        assert response.status_code == 401
