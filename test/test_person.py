"""Test functions for the person route"""

import pytest

from app import schemas
from test.conftest import compare


class TestGet:

    def test_get_all(
        self,
        authorized_client1,
        test_user1: dict,
        test_persons,
    ):
        response = authorized_client1.get("/persons")
        persons = [schemas.Person(**person) for person in response.json()]
        compare(persons, [person for person in test_persons if person.owner_id == test_user1["id"]])
        assert response.status_code == 200

    def test_get_all_unauthorised_user(
        self,
        client,
        test_persons,
    ) -> None:
        response = client.get("/persons/")
        assert response.status_code == 401

    def test_get_one(
        self,
        authorized_client1,
        test_persons,
    ) -> None:
        response = authorized_client1.get(f"/persons/{test_persons[0].id}")
        assert response.status_code == 200
        compare(schemas.Person(**response.json()), test_persons[0])

    def test_get_one_unauthorised_user(
        self,
        client,
        test_persons,
    ) -> None:
        response = client.get(f"/persons/{test_persons[0].id}")
        assert response.status_code == 401

    def test_incorrect_user_get_one(
        self,
        authorized_client2,
        test_persons,
    ) -> None:
        response = authorized_client2.get(f"/persons/{test_persons[0].id}")
        assert response.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_persons,
    ) -> None:
        response = authorized_client1.get(f"/persons/100")
        assert response.status_code == 404


class TestPost:

    @pytest.mark.parametrize(
        "first_name, last_name, email, phone, linkedin_url, company_id",
        [
            ["John", "Doe", "john.doe@example.com", "1234567890", "https://linkedin.com/in/johndoe", 1],
            ["Jane", "Smith", "jane.smith@example.com", None, "https://linkedin.com/in/janesmith", 2],
            ["Mike", "Taylor", None, "9876543210", None, 1],
            ["Emily", "Davis", "emily.davis@example.com", None, None, 2],
            ["Chris", "Brown", None, None, "https://linkedin.com/in/chrisbrown", 1],
        ],
    )
    def test_success(
        self,
        first_name,
        last_name,
        email,
        phone,
        linkedin_url,
        company_id,
        authorized_client1,
        test_user1: dict,
        test_companies,
    ):
        person_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "linkedin_url": linkedin_url,
            "company_id": company_id,
        }
        response = authorized_client1.post("/persons", json=person_data)
        created_person = schemas.PersonOut(**response.json())
        assert response.status_code == 201
        # compare(
        #     person_data,
        #     created_person,
        # )
        assert created_person.owner_id == test_user1["id"]

    def test_unauthorised(
        self,
        client,
    ) -> None:
        response = client.post("/persons", json={})
        assert response.status_code == 401


class TestDelete:

    def test_success(
        self,
        authorized_client1,
        test_persons,
    ) -> None:
        response = authorized_client1.delete(f"/persons/{test_persons[0].id}")
        assert response.status_code == 204

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.delete(f"/persons/1000")
        assert response.status_code == 404

    def test_incorrect_user(
        self,
        authorized_client2,
        test_persons,
    ) -> None:
        response = authorized_client2.delete(f"/persons/{test_persons[0].id}")
        assert response.status_code == 403

    def test_unauthorized_user(
        self,
        client,
        test_persons,
    ) -> None:
        response = client.delete(f"/persons/{test_persons[0].id}")
        assert response.status_code == 401


# --------------------------------------------------- UPDATING POSTS ---------------------------------------------------


class TestPut:

    def test_success(
        self,
        authorized_client1,
        test_user1,
        test_persons,
    ) -> None:
        person_data = {
            "first_name": "OX",
            "id": test_persons[0].id,
        }
        response = authorized_client1.put(f"/persons/{person_data['id']}", json=person_data)
        updated_person = schemas.PersonOut(**response.json())
        assert response.status_code == 200
        compare(person_data, updated_person)

    def test_empty(
        self,
        authorized_client1,
        test_persons,
    ) -> None:
        res = authorized_client1.put(f"/persons/{test_persons[0].id}", json={})
        assert res.status_code == 400

    def test_unauthorized_user(
        self,
        client,
        test_persons,
    ) -> None:
        person_data = {
            "postcode": "OX5 1HP",
            "id": test_persons[0].id,
        }
        res = client.put(f"/persons/{test_persons[0].id}", json=person_data)
        assert res.status_code == 401

    def test_incorrect_user(
        self,
        authorized_client2,
        test_persons,
    ) -> None:
        person_data = {
            "postcode": "OX5 1HP",
            "id": test_persons[0].id,
        }
        res = authorized_client2.put(f"/persons/{test_persons[0].id}", json=person_data)
        assert res.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_persons,
    ) -> None:
        res = authorized_client1.put(f"/persons/8000000", json={})
        assert res.status_code == 404
