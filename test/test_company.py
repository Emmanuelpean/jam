"""Test functions for the company route"""

import pytest

from app import schemas
from test.conftest import compare


class TestGet:

    def test_get_all(
        self,
        authorized_client1,
        test_user1: dict,
        test_companies,
    ):
        response = authorized_client1.get("/companies")
        companies = [schemas.Company(**company) for company in response.json()]
        compare(companies, [company for company in test_companies if company.owner_id == test_user1["id"]])
        assert response.status_code == 200

    def test_get_all_unauthorised_user(
        self,
        client,
        test_companies,
    ) -> None:
        response = client.get("/companies/")
        assert response.status_code == 401

    def test_get_one(
        self,
        authorized_client1,
        test_companies,
    ) -> None:
        response = authorized_client1.get(f"/companies/{test_companies[0].id}")
        assert response.status_code == 200
        compare(schemas.Company(**response.json()), test_companies[0])

    def test_get_one_unauthorised_user(
        self,
        client,
        test_companies,
    ) -> None:
        response = client.get(f"/companies/{test_companies[0].id}")
        assert response.status_code == 401

    def test_incorrect_user_get_one(
        self,
        authorized_client2,
        test_companies,
    ) -> None:
        response = authorized_client2.get(f"/companies/{test_companies[0].id}")
        assert response.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_companies,
    ) -> None:
        response = authorized_client1.get(f"/companies/100")
        assert response.status_code == 404


class TestPost:

    @pytest.mark.parametrize(
        "name, description, url",
        [
            ["Oxford PV", "an Oxford company", None],
            ["Oxford PV", None, "oxfordpv.com"],
            ["Oxford PV", None, None],
        ],
    )
    def test_success(
        self,
        name,
        description,
        url,
        authorized_client1,
        test_user1: dict,
    ):
        company_data = {"name": name, "description": description, "url": url}
        response = authorized_client1.post("/companies", json=company_data)
        created_company = schemas.CompanyOut(**response.json())
        assert response.status_code == 201
        compare(
            company_data,
            created_company,
        )
        assert created_company.owner_id == test_user1["id"]

    def test_unauthorised(
        self,
        client,
    ) -> None:
        response = client.post("/companies", json={})
        assert response.status_code == 401


class TestDelete:

    def test_success(
        self,
        authorized_client1,
        test_companies,
    ) -> None:
        response = authorized_client1.delete(f"/companies/{test_companies[0].id}")
        assert response.status_code == 204

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.delete(f"/companies/1000")
        assert response.status_code == 404

    def test_incorrect_user(
        self,
        authorized_client2,
        test_companies,
    ) -> None:
        response = authorized_client2.delete(f"/companies/{test_companies[0].id}")
        assert response.status_code == 403

    def test_unauthorized_user(
        self,
        client,
        test_companies,
    ) -> None:
        response = client.delete(f"/companies/{test_companies[0].id}")
        assert response.status_code == 401


# --------------------------------------------------- UPDATING POSTS ---------------------------------------------------


class TestPut:

    def test_success(
        self,
        authorized_client1,
        test_user1,
        test_companies,
    ) -> None:
        company_data = {
            "name": "OX",
            "id": test_companies[0].id,
        }
        response = authorized_client1.put(f"/companies/{company_data['id']}", json=company_data)
        updated_company = schemas.CompanyOut(**response.json())
        assert response.status_code == 200
        compare(company_data, updated_company)

    def test_empty(
        self,
        authorized_client1,
        test_companies,
    ) -> None:
        res = authorized_client1.put(f"/companies/{test_companies[0].id}", json={})
        assert res.status_code == 400

    def test_unauthorized_user(
        self,
        client,
        test_companies,
    ) -> None:
        company_data = {
            "postcode": "OX5 1HP",
            "id": test_companies[0].id,
        }
        res = client.put(f"/companies/{test_companies[0].id}", json=company_data)
        assert res.status_code == 401

    def test_incorrect_user(
        self,
        authorized_client2,
        test_companies,
    ) -> None:
        company_data = {
            "postcode": "OX5 1HP",
            "id": test_companies[0].id,
        }
        res = authorized_client2.put(f"/companies/{test_companies[0].id}", json=company_data)
        assert res.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_companies,
    ) -> None:
        res = authorized_client1.put(f"/companies/8000000", json={})
        assert res.status_code == 404
