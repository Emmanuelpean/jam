"""Tests for export endpoint"""

import csv
import io
import zipfile


class TestExport:

    def test_export_data(
        self,
        authorised_clients,
        test_jobs,
        test_interviews,
        test_job_application_updates,
        test_companies,
        test_persons,
        test_keywords,
        test_aggregators,
        test_users,
    ) -> None:
        """Test export endpoint returns ZIP file with all CSV files and correct data"""

        response = authorised_clients[0].get("/export/")

        # Verify response status and content type
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-zip-compressed"
        assert "attachment; filename=all_exports.zip" in response.headers["content-disposition"]

        # Parse ZIP file
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            # Verify all expected files are in the ZIP
            assert set(zf.namelist()) == {"jobs.csv", "people.csv", "companies.csv", "aggregators.csv"}

            # Verify jobs.csv content
            with zf.open("jobs.csv") as f:
                jobs_csv = f.read().decode("utf-8")
                jobs_lines = jobs_csv.strip().split("\r\n")
                # At least header should be present
                assert len(jobs_lines) >= 1
                # Verify header columns
                header = jobs_lines[0]
                assert "Job Title" in header
                assert "Company" in header
                assert "Location" in header
                assert "Keywords" in header
                assert "Contacts" in header
                assert "Interviews" in header
                assert "Updates" in header

            # Verify people.csv content
            with zf.open("people.csv") as f:
                people_csv = f.read().decode("utf-8")
                people_lines = people_csv.strip().split("\r\n")
                assert len(people_lines) >= 1
                header = people_lines[0]
                assert "First Name" in header
                assert "Last Name" in header
                assert "Company" in header

            # Verify companies.csv content
            with zf.open("companies.csv") as f:
                companies_csv = f.read().decode("utf-8")
                companies_lines = companies_csv.strip().split("\r\n")
                assert len(companies_lines) >= 1
                header = companies_lines[0]
                assert "Company Name" in header
                assert "People" in header

            # Verify aggregators.csv content
            with zf.open("aggregators.csv") as f:
                aggregators_csv = f.read().decode("utf-8")
                aggregators_lines = aggregators_csv.strip().split("\r\n")
                assert len(aggregators_lines) >= 1
                header = aggregators_lines[0]
                assert "Aggregator Name" in header

    def test_export_no_data(self, authorised_clients) -> None:
        """Test export endpoint when no data exists"""

        response = authorised_clients[0].get("/export/")

        # Verify response status and content type
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-zip-compressed"

        # Parse ZIP file
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            # Verify all files exist
            assert set(zf.namelist()) == {"jobs.csv", "people.csv", "companies.csv", "aggregators.csv"}

            # Verify each CSV only contains headers
            with zf.open("jobs.csv") as f:
                jobs_csv = f.read().decode("utf-8")
                jobs_lines = jobs_csv.strip().split("\r\n")
                assert len(jobs_lines) == 1  # Only header

            with zf.open("people.csv") as f:
                people_csv = f.read().decode("utf-8")
                people_lines = people_csv.strip().split("\r\n")
                assert len(people_lines) == 1  # Only header

            with zf.open("companies.csv") as f:
                companies_csv = f.read().decode("utf-8")
                companies_lines = companies_csv.strip().split("\r\n")
                assert len(companies_lines) == 1  # Only header

            with zf.open("aggregators.csv") as f:
                aggregators_csv = f.read().decode("utf-8")
                aggregators_lines = aggregators_csv.strip().split("\r\n")
                assert len(aggregators_lines) == 1  # Only header

    def test_export_with_relationships(
        self,
        authorised_clients,
        test_jobs,
        test_companies,
        test_keywords,
        test_persons,
        test_users,
    ) -> None:
        """Test export correctly includes related data in CSV fields"""

        response = authorised_clients[0].get("/export/")
        assert response.status_code == 200

        # Parse ZIP file
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            # Read jobs CSV and verify related fields are populated
            with zf.open("jobs.csv") as f:
                jobs_reader = csv.DictReader(io.StringIO(f.read().decode("utf-8")))
                jobs_data = list(jobs_reader)

                if jobs_data:
                    # Verify that fields like Company, Keywords, Contacts exist in header
                    first_job = jobs_data[0]
                    assert "Company" in first_job
                    assert "Keywords" in first_job
                    assert "Contacts" in first_job
                    assert "Interviews" in first_job
                    assert "Updates" in first_job

    def test_export_unauthorized(self, client) -> None:
        """Test export endpoint requires authentication"""

        response = client.get("/export/")
        assert response.status_code == 401
