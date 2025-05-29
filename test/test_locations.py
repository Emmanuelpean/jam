"""Test functions for the location route"""

import pytest

from app import schemas
from test.conftest import compare


class TestGet:

    def test_get_all(
        self,
        authorized_client1,
        test_user1: dict,
        test_locations,
    ):
        response = authorized_client1.get("/locations")
        locations = [schemas.Location(**location) for location in response.json()]
        compare(locations, [location for location in test_locations if location.owner_id == test_user1["id"]])
        assert response.status_code == 200

    def test_get_all_unauthorised_user(
        self,
        client,
        test_locations,
    ) -> None:
        response = client.get("/locations/")
        assert response.status_code == 401

    def test_get_one(
        self,
        authorized_client1,
        test_locations,
    ) -> None:
        response = authorized_client1.get(f"/locations/{test_locations[0].id}")
        assert response.status_code == 200
        compare(schemas.Location(**response.json()), test_locations[0])

    def test_get_one_unauthorised_user(
        self,
        client,
        test_locations,
    ) -> None:
        response = client.get(f"/locations/{test_locations[0].id}")
        assert response.status_code == 401

    def test_incorrect_user_get_one(
        self,
        authorized_client2,
        test_locations,
    ) -> None:
        response = authorized_client2.get(f"/locations/{test_locations[0].id}")
        assert response.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_locations,
    ) -> None:
        response = authorized_client1.get(f"/locations/100")
        assert response.status_code == 404


class TestPost:

    @pytest.mark.parametrize(
        "postcode, city, country, remote",
        [
            ["OX5 1HN", None, None, False],
            [None, "Oxford", None, False],
            [None, None, "UK", False],
            [None, None, None, True],
            ["OX5 1HN", None, None, True],
        ],
    )
    def test_success(
        self,
        postcode,
        city,
        country,
        remote,
        authorized_client1,
        test_user1: dict,
    ):
        location_data = {"postcode": postcode, "city": city, "country": country, "remote": remote}
        response = authorized_client1.post("/locations", json=location_data)
        created_location = schemas.LocationOut(**response.json())
        assert response.status_code == 201
        compare(
            location_data,
            created_location,
        )
        assert created_location.owner_id == test_user1["id"]

    def test_unauthorised(
        self,
        client,
    ) -> None:
        location_data = {"postcode": "OX5 1HN", "city": None, "country": None, "remote": None}
        response = client.post("/locations", json=location_data)
        assert response.status_code == 401


class TestDelete:

    def test_success(
        self,
        authorized_client1,
        test_locations,
    ) -> None:
        response = authorized_client1.delete(f"/locations/{test_locations[0].id}")
        assert response.status_code == 204

    def test_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = authorized_client1.delete(f"/locations/1000")
        assert response.status_code == 404

    def test_incorrect_user(
        self,
        authorized_client2,
        test_locations,
    ) -> None:
        response = authorized_client2.delete(f"/locations/{test_locations[0].id}")
        assert response.status_code == 403

    def test_unauthorized_user(
        self,
        client,
        test_locations,
    ) -> None:
        response = client.delete(f"/locations/{test_locations[0].id}")
        assert response.status_code == 401


# --------------------------------------------------- UPDATING POSTS ---------------------------------------------------


class TestPut:

    def test_success(
        self,
        authorized_client1,
        test_user1,
        test_locations,
    ) -> None:
        location_data = {
            "postcode": "OX5 1HP",
            "id": test_locations[0].id,
        }
        response = authorized_client1.put(f"/locations/{location_data['id']}", json=location_data)
        print(response.json())
        updated_location = schemas.LocationOut(**response.json())
        assert response.status_code == 200
        for attr in location_data:
            assert getattr(updated_location, attr) == location_data[attr]

    def test_unauthorized_user(
        self,
        client,
        test_locations,
    ) -> None:
        location_data = {
            "postcode": "OX5 1HP",
            "id": test_locations[0].id,
        }
        res = client.put(f"/locations/{test_locations[0].id}", json=location_data)
        assert res.status_code == 401

    def test_incorrect_user(
        self,
        authorized_client2,
        test_locations,
    ) -> None:
        location_data = {
            "postcode": "OX5 1HP",
            "id": test_locations[0].id,
        }
        res = authorized_client2.put(f"/locations/{test_locations[0].id}", json=location_data)
        assert res.status_code == 403

    def test_non_exist(
        self,
        authorized_client1,
        test_locations,
    ) -> None:
        res = authorized_client1.put(f"/locations/8000000", json={})
        assert res.status_code == 404
