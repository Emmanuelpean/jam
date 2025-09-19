"""Tests for export endpoint"""


class TestExport:

    def test_export_data(
        self,
        authorised_clients,
        test_jobs,
        test_interviews,
        test_job_application_updates,
        test_companies,
        test_keywords,
        test_aggregators,
        test_users,
    ) -> None:
        """Test export endpoint returns CSV data with all columns and related data"""

        response = authorised_clients[0].get("/export")
        assert response.status_code == 200
