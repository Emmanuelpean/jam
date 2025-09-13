"""
Test module for API router endpoints covering CRUD operations for JAM entities.

This module contains comprehensive test classes for all API endpoints, organised into simple tables
(companies, keywords, aggregators, locations, files) and complex tables with relationships
(persons, jobs, job applications, interviews, job application updates). Each test class inherits
from CRUDTestBase to ensure consistent testing of standard CRUD operations, including authorisation,
validation, and error handling. Additional custom endpoint tests are included where applicable.
"""

from app import schemas
from conftest import CRUDTestBase
from tests.utils.table_data import (
    COMPANY_DATA,
    LOCATION_DATA,
    PERSON_DATA,
    AGGREGATOR_DATA,
    KEYWORD_DATA,
    FILE_DATA,
    JOB_DATA,
    INTERVIEW_DATA,
    JOB_APPLICATION_UPDATE_DATA,
)



class TestLatestUpdatesRouter:
    """Test class for the updates router endpoints"""

    def test_get_all_updates_basic_functionality(
            self, authorised_clients, test_interviews, test_job_application_updates
    ) -> None:
        """Test get_all_updates endpoint returns unified updates"""
        response = authorised_clients[0].get("/latest_updates/")
        assert response.status_code == 200

        updates = response.json()
        assert isinstance(updates, list)

        # Verify each update has the expected structure
        for update in updates:
            assert "date" in update
            assert "type" in update
            assert "job_title" in update

            # Verify type is one of the expected values
            assert update["type"] in ["Application", "Interview", "Job Application Update"]

            # Verify date format (should be ISO datetime string)
            assert isinstance(update["date"], str)

        # Verify updates are sorted by date (most recent first)
        if len(updates) > 1:
            for i in range(len(updates) - 1):
                current_date = updates[i]["date"]
                next_date = updates[i + 1]["date"]
                assert current_date >= next_date

    def test_get_all_updates_with_limit(self, authorised_clients) -> None:
        """Test get_all_updates endpoint with custom limit parameter"""
        # Test with small limit
        response = authorised_clients[0].get("/latest_updates/?limit=5")
        assert response.status_code == 200

        updates = response.json()
        assert len(updates) <= 5

        # Test with larger limit
        response = authorised_clients[0].get("/latest_updates/?limit=50")
        assert response.status_code == 200

        updates_large = response.json()
        assert len(updates_large) >= len(updates)  # Should return same or more results

    def test_get_all_updates_unauthorized(self, client) -> None:
        """Test that unauthorized requests are rejected"""
        response = client.get("/latest_updates/")
        assert response.status_code == 401


class TestGeneralRouter:
    """Test class for general router endpoints"""

    def test_get_all_updates_with_job_applications(self, test_users, authorised_clients, test_job_applications) -> None:
        """Test get_all_updates returns job applications with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        assert all(d["type"] == "Application" for d in data)
        assert len(data) == len(test_job_applications)
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})

    def test_get_all_updates_with_interviews(self, test_users, authorised_clients, test_interviews) -> None:
        """Test get_all_updates returns interviews with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        job_applications = [d for d in data if d["type"] == "Application"]
        interviews = [d for d in data if d["type"] == "Interview"]
        assert len(job_applications) == 8
        assert len(interviews) == 12
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})

    def test_get_all_updates_with_interviews_updates(
            self, test_users, authorised_clients, test_interviews, test_job_application_updates
    ) -> None:
        """Test get_all_updates returns interviews with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        job_applications = [d for d in data if d["type"] == "Application"]
        interviews = [d for d in data if d["type"] == "Interview"]
        updates = [d for d in data if d["type"] == "Job Application Update"]
        assert len(updates) == 10
        assert len(job_applications) == 3
        assert len(interviews) == 7
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})
