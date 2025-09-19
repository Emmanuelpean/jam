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

    def test_export_no_data(self, authorised_clients) -> None:
        """Test export endpoint when no jobs exist"""

        response = authorised_clients[0].get("/export")
        assert response.status_code == 200
        assert response.content.decode() == (
            "title,description,salary_min,salary_max,personal_rating,url,deadline,note,"
            "attendance_type,application_date,application_url,application_status,"
            "application_note,applied_via,created_at,modified_at,Company,Location,"
            "Source Aggregator,Application Aggregator,Keywords,Contacts,Interviews,Updates\r\n"
        )
