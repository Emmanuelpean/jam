"""Test functions for the aggregator_website route"""

import pytest
from app import schemas
from test.conftest import compare


class TestGet:

    def test_get_all(
        self,
        authorized_client1,
        test_aggregators,
    ):
        response = authorized_client1.get("/aggregators")
        aggregators = [schemas.Aggregator(**website) for website in response.json()]
        compare(aggregators, test_aggregators)
        assert response.status_code == 200

    def test_get_all_unauthorised_user(
        self,
        client,
        test_aggregators,
    ) -> None:
        response = client.get("/aggregators")
        assert response.status_code == 401

    def test_get_one(
        self,
        authorized_client1,
        test_aggregators,
    ) -> None:
        response = authorized_client1.get(f"/aggregators/{test_aggregators[0].id}")
        assert response.status_code == 200
        compare(schemas.Aggregator(**response.json()), test_aggregators[0])

    def test_get_one_unauthorised_user(
        self,
        client,
        test_aggregators,
    ) -> None:
        response = client.get(f"/aggregators/{test_aggregators[0].id}")
        assert response.status_code == 401

    def test_non_exist(
        self,
        authorized_client1,
        test_aggregators,
    ) -> None:
        response = authorized_client1.get(f"/aggregators/1000")
        assert response.status_code == 404


class TestPost:

    @pytest.mark.parametrize(
        "name, url",
        [
            ["LinkedIn", "https://linkedin.com"],
            ["Indeed", "https://indeed.com"],
            ["Glassdoor", "https://glassdoor.com"],
        ],
    )
    def test_success(
        self,
        name,
        url,
        authorized_client1,
    ):
        website_data = {
            "name": name,
            "url": url,
        }
        response = authorized_client1.post("/aggregators", json=website_data)
        created_website = schemas.AggregatorOut(**response.json())
        assert response.status_code == 201
        assert created_website.name == name
        assert created_website.url == url

    def test_unauthorised(
        self,
        client,
    ) -> None:
        response = client.post("/aggregators", json={})
        assert response.status_code == 401


class TestDelete:

    def test_success(
        self,
        authorized_client1,
        test_aggregators,
    ) -> None:
        response = authorized_client1.delete(f"/aggregators/{test_aggregators[0].id}")
        assert response.status_code == 204

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.delete(f"/aggregators/1000")
        assert response.status_code == 404

    def test_unauthorized_user(
        self,
        client,
        test_aggregators,
    ) -> None:
        response = client.delete(f"/aggregators/{test_aggregators[0].id}")
        assert response.status_code == 401


class TestPut:

    def test_success(
        self,
        authorized_client1,
        test_aggregators,
    ) -> None:
        updated_website_data = {
            "name": "Updated LinkedIn",
            "url": "https://updated-linkedin.com",
            "id": test_aggregators[0].id,
        }
        response = authorized_client1.put(f"/aggregators/{updated_website_data['id']}", json=updated_website_data)
        updated_website = schemas.AggregatorOut(**response.json())
        assert response.status_code == 200
        assert updated_website.name == "Updated LinkedIn"
        assert updated_website.url == "https://updated-linkedin.com"

    def test_empty(
        self,
        authorized_client1,
        test_aggregators,
    ) -> None:
        response = authorized_client1.put(f"/aggregators/{test_aggregators[0].id}", json={})
        assert response.status_code == 400

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.put(f"/aggregators/1000", json={})
        assert response.status_code == 404
