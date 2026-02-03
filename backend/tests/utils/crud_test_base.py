"""Base class for CRUD tests on FastAPI routes."""

import datetime as dt
from typing import Any

import pytest
from fastapi import status
from requests import Response
from starlette.testclient import TestClient

from app import models
from tests.utils import test_data as td


def assert_ownership(item: list | dict, owner_id: int) -> None:
    """Assert that all items in a list belong to the specified owner."""
    if isinstance(item, dict):
        if "owner_id" in item:
            assert item["owner_id"] == owner_id
        for key in item:
            assert_ownership(item[key], owner_id)
    if isinstance(item, list):
        for subitem in item:
            assert_ownership(subitem, owner_id)


class CRUDTestBase:
    """Base class for CRUD tests on FastAPI routes.

    Subclasses must override:
    - endpoint: str - base URL path for the resource (e.g. "/aggregators")
    - create_schema: Pydantic model class for creation validation (e.g. schemas.AggregatorCreate)
    - out_schema: Pydantic model class for output validation (e.g. schemas.AggregatorOut)
    - test_data_ref: str - name of pytest fixture providing list of test objects
    - update_data: dict - example data for updating an existing object
    - create_data: list[dict] - example data for creating new objects
    - required_fixture: str or list[str] - name(s) of pytest fixture(s) for the post operations
    - get_unauthorised_fixture: str - name of pytest fixture providing data for access tests with incorrect ownership
    - unauthorised_data_fixture: str - name of pytest fixture providing data for creation tests with incorrect ownership
    - admin_only: bool - if True, only admin users can access the endpoint
    - actions_to_test: list[str] - which CRUD actions to test (any subset of ["get", "post", "put", "delete"])
    """

    endpoint: str = ""
    create_schema = None
    out_schema = None
    test_data_ref: str = ""
    update_data: dict[str, str | int] = None
    create_data: list[dict] = None
    required_fixture: str = None
    get_unauthorised_fixture: str = None
    unauthorised_data_fixture = None
    admin_only: bool = False
    actions_to_test: list[str] = ["get", "post", "put", "delete"]

    def check_output(
        self,
        test_data: Any,
        response_data: list[dict] | dict,
    ):
        """Check that the output of a test matches the test data."""
        if isinstance(test_data, list) and isinstance(response_data, list):
            assert len(test_data) == len(response_data)
            for d1, d2 in zip(test_data, response_data):
                return self.check_output(d1, d2)

        if isinstance(response_data, dict):
            response_data = self.out_schema(**response_data)

        if isinstance(test_data, dict):
            items = test_data.items()
        else:
            items = vars(test_data).items()

        for key, value in items:
            if key[0] != "_" and key in response_data:
                response_value = getattr(response_data, key)
                if isinstance(value, models.Base) or isinstance(value, list):
                    self.check_output(value, response_value)
                elif key == "date" and isinstance(value, str):
                    if isinstance(response_value, dt.datetime):
                        parsed_value = dt.datetime.fromisoformat(value)
                        if response_value.tzinfo is not None and parsed_value.tzinfo is None:
                            parsed_value = parsed_value.replace(tzinfo=dt.timezone.utc)
                        elif response_value.tzinfo is None and parsed_value.tzinfo is not None:
                            parsed_value = parsed_value.replace(tzinfo=None)
                        assert parsed_value == response_value
                    else:
                        assert value == response_value
                else:
                    try:
                        assert value == response_value
                    except Exception:
                        print(value)
                        print(response_value)
                        raise AssertionError

        return None

    # -------------------------------------------------- CRUD METHODS --------------------------------------------------

    def get_all(self, client) -> Response:
        """Helper method to get all items from the endpoint."""
        return client.get(self.endpoint)

    def get_bulk(self, client, item_ids) -> Response:
        """Helper method to get bulk items from the endpoint."""
        strings = ["ids=" + str(i) for i in item_ids]
        return client.get(f"{self.endpoint}/?{'&'.join(strings)}")

    def get_one(self, client, item_id) -> Response:
        """Helper method to get one item from the endpoint."""
        return client.get(f"{self.endpoint}/{item_id}")

    def post(self, client, data) -> Response:
        """Helper method to post a new item to the endpoint."""
        return client.post(self.endpoint, json=data)

    def put(self, client: TestClient, item_id: int, data) -> Response:
        """Helper method to update an existing item in the endpoint."""
        return client.put(f"{self.endpoint}/{item_id}", json=data)

    def delete(self, client, item_id) -> Response:
        """Helper method to delete an existing item from the endpoint."""
        return client.delete(f"{self.endpoint}/{item_id}")

    # ----------------------------------------------------- CLIENTS ----------------------------------------------------

    def _get_authorised_client(self, authorised_clients) -> TestClient:
        """Get the appropriate authorised client based on admin_only setting."""
        if self.admin_only:
            return authorised_clients[td.ADMIN_USER_INDEX]
        else:
            return authorised_clients[td.REGULAR_USER_INDEX]

    def _get_admin_unauthorised_client(self, authorised_clients) -> TestClient:
        """Get a client that should be denied access."""
        if self.admin_only:
            return authorised_clients[td.REGULAR_USER_INDEX]
        else:
            return authorised_clients[td.ADMIN_USER_INDEX]

    def _get_admin_authorised_user(self, test_users) -> models.User:
        """Get the appropriate authorised user based on admin_only setting."""
        if self.admin_only:
            return test_users[td.ADMIN_USER_INDEX]
        else:
            return test_users[td.REGULAR_USER_INDEX]

    def get_user_data(self, test_users, data: list) -> list:
        """Get create_data filtered by owner_id based on admin_only setting."""
        user = self._get_admin_authorised_user(test_users)
        filtered_data = []
        for d in data:
            if isinstance(d, dict):
                owner_condition = "owner_id" in d and d["owner_id"] == user.id
            else:
                owner_condition = hasattr(d, "owner_id") and d.owner_id == user.id

            if not self.admin_only:
                if owner_condition:
                    filtered_data.append(d)
            else:
                filtered_data.append(d)

        return filtered_data

    @pytest.fixture(autouse=True)
    def setup_method(self, request) -> None:
        """Fixture that runs before each test method."""
        if isinstance(self.required_fixture, list):
            for fixture in self.required_fixture:
                request.getfixturevalue(fixture)

    @pytest.fixture
    def test_data(self, request, test_users) -> list:
        """Fixture to get the test data from the specified fixture name."""
        return self.get_user_data(test_users, request.getfixturevalue(self.test_data_ref))

    # ----------------------------------------------------- GET ALL ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_authorised(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that an authorised users can successfully retrieve all items from the endpoint."""
        client = self._get_authorised_client(authorised_clients)
        response = self.get_all(client)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_data, response.json())

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_unauthenticated(
        self,
        client: TestClient,
        test_data,
    ) -> None:
        """Test that unauthenticated requests to get all items are rejected."""
        response = self.get_all(client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_non_admin(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that non admin user requests to get all items are rejected for admin_only endpoints."""
        if self.admin_only:
            client = self._get_admin_unauthorised_client(authorised_clients)
            response = self.get_all(client)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_data_only_authorised(
        self,
        authorised_clients,
        request,
    ) -> None:
        """Test that users only see data they own when retrieving all items (non-admin endpoints only)."""
        if not self.admin_only and self.get_unauthorised_fixture:
            owner_id = request.getfixturevalue(self.get_unauthorised_fixture)[1]
            response = self.get_all(authorised_clients[owner_id - 1])
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            print(data)
            if data:
                assert_ownership(data, owner_id)

    # ----------------------------------------------------- GET ONE ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_success(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that an authorised users can successfully retrieve a specific item by ID."""
        client = self._get_authorised_client(authorised_clients)
        response = self.get_one(client, test_data[0].id)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_data[0], response.json())

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_unauthenticated(
        self,
        client,
        test_data,
    ) -> None:
        """Test that unauthenticated requests to get a specific item are rejected."""
        response = self.get_one(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_incorrect_user(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that users are denied access to items they don't have permission to view."""
        client = self._get_admin_unauthorised_client(authorised_clients)
        response = self.get_one(client, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_non_exist(
        self,
        authorised_clients,
    ) -> None:
        """Test that requests for non-existent items return a 404 error."""
        client = self._get_authorised_client(authorised_clients)
        response = self.get_one(client, 0)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    @pytest.mark.requires_actions("post")
    def test_post_success(
        self,
        authorised_clients,
        test_users,
    ) -> None:
        """Test that authorised users can successfully create new items."""
        client = self._get_authorised_client(authorised_clients)
        for create_data in self.get_user_data(test_users, self.create_data):
            create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
            response = self.post(client, create_data)
            assert response.status_code == status.HTTP_201_CREATED
            self.check_output(create_data, response.json())

    @pytest.mark.requires_actions("post")
    def test_post_unauthenticated(
        self,
        client,
    ) -> None:
        """Test that unauthenticated requests to create items are rejected."""
        response = self.post(client, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("post")
    def test_post_non_admin(
        self,
        authorised_clients,
        test_users,
    ) -> None:
        """Test that non-admin users are denied access to create items on admin-only endpoints."""
        if self.admin_only:
            client = self._get_admin_unauthorised_client(authorised_clients)
            for create_data in self.get_user_data(test_users, self.create_data):
                create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
                response = self.post(client, create_data)
                assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("post")
    def test_post_data_only_authorised(
        self,
        authorised_clients,
        request,
    ) -> None:
        """Test that users can successfully create data they own on non-admin endpoints."""
        if not self.admin_only and self.unauthorised_data_fixture:
            data, owner_id = request.getfixturevalue(self.unauthorised_data_fixture)[:2]
            for datum in data:
                datum = {key: value for key, value in datum.items() if key not in ("id", "owner_id")}
                response = self.post(authorised_clients[owner_id - 1], datum)
                assert response.status_code == status.HTTP_201_CREATED
                assert_ownership(data, owner_id)

    # ------------------------------------------------------- PUT ------------------------------------------------------

    @pytest.mark.requires_actions("put")
    def test_put_success(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that authorised users can successfully update existing items."""
        client = self._get_authorised_client(authorised_clients)
        response = self.put(client, self.update_data.get("id"), self.update_data)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(self.update_data, response.json())

    @pytest.mark.requires_actions("put")
    def test_put_empty_body(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that PUT requests with empty request bodies are rejected."""
        client = self._get_authorised_client(authorised_clients)
        response = self.put(client, test_data[0].id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.requires_actions("put")
    def test_put_non_exist(self, authorised_clients) -> None:
        """Test that PUT requests for non-existent items return a 404 error."""
        client = self._get_authorised_client(authorised_clients)
        response = self.put(client, 0, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.requires_actions("put")
    def test_put_unauthenticated(
        self,
        client,
        test_data,
    ) -> None:
        """Test that unauthenticated requests to update items are rejected."""
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("put")
    def test_put_forbidden(self, authorised_clients, test_data) -> None:
        """Test that users are denied access to update items they don't have permission to modify."""
        client = self._get_admin_unauthorised_client(authorised_clients)
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    @pytest.mark.requires_actions("delete")
    def test_delete_success(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that authorised users can successfully delete existing items."""
        client = self._get_authorised_client(authorised_clients)
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.requires_actions("delete")
    def test_delete_non_exist(
        self,
        authorised_clients,
    ) -> None:
        """Test that DELETE requests for non-existent items return a 404 error."""
        client = self._get_authorised_client(authorised_clients)
        response = self.delete(client, 0)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.requires_actions("delete")
    def test_delete_unauthenticated(
        self,
        client,
        test_data,
    ) -> None:
        """Test that unauthenticated requests to delete items are rejected."""
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("delete")
    def test_delete_forbidden(
        self,
        authorised_clients,
        test_data,
    ) -> None:
        """Test that users are denied access to delete items they don't have permission to remove."""
        client = self._get_admin_unauthorised_client(authorised_clients)
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
