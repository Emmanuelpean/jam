"""Test functions for the job_website route"""

import pytest
from app import schemas
from test.conftest import compare


class TestGet:

    def test_get_all(
        self,
        authorized_client1,
        test_jobs,
    ):
        response = authorized_client1.get("/jobs")
        jobs = [schemas.Job(**website) for website in response.json()]
        compare(jobs, test_jobs)
        assert response.status_code == 200

    def test_get_all_unauthorised_user(
        self,
        client,
        test_jobs,
    ) -> None:
        response = client.get("/jobs")
        assert response.status_code == 401

    def test_get_one(
        self,
        authorized_client1,
        test_jobs,
    ) -> None:
        response = authorized_client1.get(f"/jobs/{test_jobs[0].id}")
        assert response.status_code == 200
        compare(schemas.Job(**response.json()), test_jobs[0])

    def test_get_one_unauthorised_user(
        self,
        client,
        test_jobs,
    ) -> None:
        response = client.get(f"/jobs/{test_jobs[0].id}")
        assert response.status_code == 401

    def test_non_exist(
        self,
        authorized_client1,
        test_jobs,
    ) -> None:
        response = authorized_client1.get(f"/jobs/1000")
        assert response.status_code == 404


class TestPost:

    @pytest.mark.parametrize(
        "job_data",
        [
            {
                "title": "Software Engineer",
                "salary_min": 50000,
                "salary_max": 100000,
                "description": "Design, develop, and maintain software solutions.",
                "personal_rating": 8,
                "url": "https://example.com/jobs/software_engineer",
            },
            {
                "title": "Data Scientist",
                "salary_min": 60000,
                "salary_max": 120000,
                "description": "Analyze complex datasets and derive insights.",
                "personal_rating": 9,
                "url": "https://example.com/jobs/data_scientist",
            },
            {
                "title": "Frontend Developer",
                "salary_min": 55000,
                "salary_max": 90000,
                "description": "Build interactive and responsive web interfaces.",
                "personal_rating": 7,
                "url": "https://example.com/jobs/frontend_developer",
            },
        ],
    )
    def test_success(
        self,
        job_data,
        authorized_client1,
        authorized_client2,
        test_companies,
    ):
        response = authorized_client1.post("/jobs", json=job_data)
        created_website = schemas.JobOut(**response.json())
        compare(job_data, created_website)
        assert response.status_code == 201

    def test_unauthorised(
        self,
        client,
    ) -> None:
        response = client.post("/jobs", json={})
        assert response.status_code == 401


class TestDelete:

    def test_success(
        self,
        authorized_client1,
        test_jobs,
    ) -> None:
        response = authorized_client1.delete(f"/jobs/{test_jobs[0].id}")
        assert response.status_code == 204

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.delete(f"/jobs/1000")
        assert response.status_code == 404

    def test_unauthorized_user(
        self,
        client,
        test_jobs,
    ) -> None:
        response = client.delete(f"/jobs/{test_jobs[0].id}")
        assert response.status_code == 401


class TestPut:

    def test_success(
        self,
        authorized_client1,
        test_jobs,
    ) -> None:
        updated_job_data = {
            "title": "Updated title",
            "url": "https://updated-linkedin.com",
            "id": test_jobs[0].id,
        }
        response = authorized_client1.put(f"/jobs/{updated_job_data['id']}", json=updated_job_data)
        updated_website = schemas.JobOut(**response.json())
        assert response.status_code == 200
        compare(updated_job_data, updated_website)

    def test_empty(
        self,
        authorized_client1,
        test_jobs,
    ) -> None:
        response = authorized_client1.put(f"/jobs/{test_jobs[0].id}", json={})
        assert response.status_code == 400

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.put(f"/jobs/1000", json={})
        assert response.status_code == 404
