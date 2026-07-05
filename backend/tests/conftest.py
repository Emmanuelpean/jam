"""
Test configuration and pytest hooks.

Fixtures are organised in the tests/fixtures/ directory:
- database.py: Database session and engine fixtures
- clients.py: API test client fixtures
- users.py: User-related fixtures
- others.py: Test data fixtures for various models

The CRUDTestBase class is in tests/utils/crud_test_base.py
"""

import os
from typing import Generic, Type, TypeVar
from unittest.mock import patch

import pytest
from pydantic import BaseModel
from requests import Response
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser

# Load fixtures from separate modules
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.clients",
    "tests.fixtures.users",
    "tests.fixtures.others",
    "tests.fixtures.emails",
    "tests.fixtures.requests",
]


# ------------------------------------------------------ FIXTURES ------------------------------------------------------


@pytest.fixture(autouse=True)
def enable_test_mode():
    """Force test_mode=True for all tests so emails are intercepted and test-only routes are active."""

    with patch("app.config.settings.test_mode", True):
        yield


@pytest.fixture(autouse=True)
def mock_captcha_verification():
    """Bypass Cloudflare Turnstile network calls in tests; production verification stays intact."""

    with patch("app.core.routers.auth.verify_captcha_token", return_value=True):
        yield


# -------------------------------------------------------- UTILS -------------------------------------------------------


def open_file(filepath: str) -> str:
    """Helper function to open a text file from the resources directory.
    :param filepath: The name of the file located in the resources directory"""

    base_dir = str(os.path.dirname(__file__))
    filepath = os.path.join(base_dir, "resources", filepath)
    with open(filepath, "r", encoding="utf8") as ofile:
        return ofile.read()


def pytest_configure(config) -> None:
    """Configure pytest to add custom markers."""

    config.addinivalue_line("markers", "requires_actions(*actions): mark test as requiring certain CRUD actions")


def pytest_collection_modifyitems(config, items) -> None:
    """Modify collected test items to skip tests based on actions_to_test setting in test classes."""

    _ = config
    for item in items:
        mark = item.get_closest_marker("requires_actions")
        if not mark:
            continue
        required_actions = set(mark.args)
        cls = getattr(item, "cls", None)
        actions_to_test = getattr(cls, "actions_to_test", [])
        if required_actions.isdisjoint(actions_to_test):
            item.add_marker(pytest.mark.skip(reason="Skipping tests as per actions_to_test setting"))


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


EntryT = TypeVar("EntryT", bound=models.CommonBase)


class CRUDTestBase(BaseTest, Generic[EntryT]):
    """Base class for CRUD tests on FastAPI routes.

    Instead of relying on shared test-data fixtures, each subclass creates only the entries it
    needs per test by overriding the creation hooks below.

    Subclasses must override:
    - endpoint: str - base URL path for the resource (e.g. "/aggregators")
    - out_schema: Pydantic model class for output validation (e.g. schemas.AggregatorOut)
    - update_data: dict - fields to change when updating an existing entry (no "id")
    - create_entry(session, owner, **overrides): create one persisted entry owned by `owner`
      (needed for the get/put/delete actions)
    - create_payload(session, owner): build a valid POST body for creating an entry owned by
      `owner`, creating any related entries as needed (needed for the "post" action)

    Subclasses may override:
    - create_schema: Pydantic model class for creation validation
    - create_unauthorised_payload(session, owner, other): a POST body linking to an entry owned by
      `other`, to assert unowned links are rejected; return None (default) to skip that test
    - admin_only: bool - if True, only admin users can access the endpoint
    - actions_to_test: list[str] - which CRUD actions to test (any subset of ["get", "post", "put", "delete"])
    - too_long_create_data: dict - a POST body with an over-length field, to assert 422
    - n_entries: int - how many entries to seed for the get-all tests"""

    endpoint: str = ""
    create_schema: Type[BaseModel] | None = None
    out_schema: Type[BaseModel] | None = None
    update_data: dict[str, str | int] = None
    admin_only: bool = False
    actions_to_test: list[str] = ["get", "post", "put", "delete"]
    too_long_create_data: dict | None = None
    n_entries: int = 2

    # ------------------------------------------------- CREATION HOOKS -------------------------------------------------

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> EntryT:
        """Create and return one persisted entry owned by `owner`. Override in subclasses."""
        raise NotImplementedError(f"{type(self).__name__} must implement create_entry")

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        """Return a valid POST body for creating an entry owned by `owner`, creating any related
        entries it references. Override in subclasses that test the "post" action."""
        raise NotImplementedError(f"{type(self).__name__} must implement create_payload")

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict | None:
        """Return a POST body that links to an entry owned by `other`, so the endpoint can be
        checked to reject unowned links. Return None (default) to skip that test."""
        return None

    def create_entries(self, session: Session, owner: FixtureUser) -> list[EntryT]:
        """Create `n_entries` entries owned by `owner` for the get-all tests."""
        return [self.create_entry(session, owner) for _ in range(self.n_entries)]

    # -------------------------------------------------- CRUD METHODS --------------------------------------------------

    def get_all(self, client: TestClient) -> Response:
        """Helper method to get all items from the endpoint."""
        return client.get(self.endpoint)

    def get_bulk(self, client: TestClient, item_ids: list[int]) -> Response:
        """Helper method to get bulk items from the endpoint."""
        strings = ["ids=" + str(i) for i in item_ids]
        return client.get(f"{self.endpoint}/?{'&'.join(strings)}")

    def get_one(self, client: TestClient, item_id: int) -> Response:
        """Helper method to get one item from the endpoint."""
        return client.get(f"{self.endpoint}/{item_id}")

    def post(self, client: TestClient, data: dict) -> Response:
        """Helper method to post a new item to the endpoint."""
        return client.post(self.endpoint, json=data)

    def put(self, client: TestClient, item_id: int, data: dict) -> Response:
        """Helper method to update an existing item in the endpoint."""
        return client.put(f"{self.endpoint}/{item_id}", json=data)

    def delete(self, client: TestClient, item_id: int) -> Response:
        """Helper method to delete an existing item from the endpoint."""
        return client.delete(f"{self.endpoint}/{item_id}")

    # ----------------------------------------------------- CLIENTS ----------------------------------------------------

    @pytest.fixture
    def authorised_user(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> FixtureUser:
        """The user whose client is used for authorised requests (admin for admin_only endpoints)."""
        return test_admin_user if self.admin_only else test_regular_user

    @pytest.fixture
    def unauthorised_user(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> FixtureUser:
        """The user whose client should be denied access (the opposite of authorised_user)."""
        return test_regular_user if self.admin_only else test_admin_user

    # ----------------------------------------------------- GET ALL ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_authorised(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that authorised users can successfully retrieve all items they own from the endpoint."""

        entries = self.create_entries(session, authorised_user)
        response = self.get_all(authorised_user.client)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= len(entries)
        if data and "id" in data[0]:
            returned_ids = {item["id"] for item in data}
            assert {entry.id for entry in entries} <= returned_ids
            self.check_output(entries[0], next(item for item in data if item["id"] == entries[0].id), self.out_schema)
        else:
            self.check_output(entries[0], data[0], self.out_schema)

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_unauthenticated(self, client: TestClient) -> None:
        """Test that unauthenticated requests to get all items are rejected."""
        response = self.get_all(client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_non_admin(self, unauthorised_user: FixtureUser) -> None:
        """Test that non-admin users requests to get all items are rejected for admin_only endpoints."""
        if self.admin_only:
            response = self.get_all(unauthorised_user.client)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_data_only_authorised(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that users only see data they own when retrieving all items (non-admin endpoints only)."""
        if self.admin_only:
            return
        self.create_entry(session, authorised_user)
        self.create_entry(session, unauthorised_user)
        response = self.get_all(authorised_user.client)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data
        assert_ownership(data, authorised_user.id)

    # ----------------------------------------------------- GET ONE ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_success(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that authorised users can successfully retrieve a specific item by ID."""
        entry = self.create_entry(session, authorised_user)
        response = self.get_one(authorised_user.client, entry.id)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(entry, response.json(), self.out_schema)

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_unauthenticated(self, session: Session, client: TestClient, authorised_user: FixtureUser) -> None:
        """Test that unauthenticated requests to get a specific item are rejected."""
        entry = self.create_entry(session, authorised_user)
        response = self.get_one(client, entry.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_incorrect_user(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that users are denied access to items they don't have permission to view."""
        entry = self.create_entry(session, authorised_user)
        response = self.get_one(unauthorised_user.client, entry.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_non_exist(self, authorised_user: FixtureUser) -> None:
        """Test that requests for non-existent items return a 404 error."""
        response = self.get_one(authorised_user.client, 0)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    @pytest.mark.requires_actions("post")
    def test_post_success(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that authorised users can successfully create new items."""
        payload = self.create_payload(session, authorised_user)
        response = self.post(authorised_user.client, payload)
        assert response.status_code == status.HTTP_201_CREATED
        self.check_output(payload, response.json(), self.out_schema)

    @pytest.mark.requires_actions("post")
    def test_post_unauthenticated(self, client: TestClient) -> None:
        """Test that unauthenticated requests to create items are rejected."""
        response = self.post(client, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("post")
    def test_post_non_admin(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that non-admin users are denied access to create items on admin-only endpoints."""
        if self.admin_only:
            payload = self.create_payload(session, authorised_user)
            response = self.post(unauthorised_user.client, payload)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("post")
    def test_post_field_too_long(self, authorised_user: FixtureUser) -> None:
        """Test that creating an item with a field exceeding its max length returns 422."""
        if self.too_long_create_data is None:
            return
        response = self.post(authorised_user.client, self.too_long_create_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.requires_actions("post")
    def test_post_unowned_link_rejected(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that creating an entry linking to a related entry the user does not own is rejected."""

        payload = self.create_unauthorised_payload(session, authorised_user, unauthorised_user)
        if payload is None:
            return
        response = self.post(authorised_user.client, payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ------------------------------------------------------- PUT ------------------------------------------------------

    @pytest.mark.requires_actions("put")
    def test_put_success(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that authorised users can successfully update existing items."""

        entry = self.create_entry(session, authorised_user)
        response = self.put(authorised_user.client, entry.id, self.update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == entry.id
        self.check_output(self.update_data, response.json(), self.out_schema)

    @pytest.mark.requires_actions("put")
    def test_put_empty_body(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that PUT requests with empty request bodies are rejected."""

        entry = self.create_entry(session, authorised_user)
        response = self.put(authorised_user.client, entry.id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.requires_actions("put")
    def test_put_non_exist(self, authorised_user: FixtureUser) -> None:
        """Test that PUT requests for non-existent items return a 404 error."""

        response = self.put(authorised_user.client, 0, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.requires_actions("put")
    def test_put_unauthenticated(self, session: Session, client: TestClient, authorised_user: FixtureUser) -> None:
        """Test that unauthenticated requests to update items are rejected."""

        entry = self.create_entry(session, authorised_user)
        response = self.put(client, entry.id, {"name": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("put")
    def test_put_forbidden(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that users are denied access to update items they don't have permission to modify."""

        entry = self.create_entry(session, authorised_user)
        response = self.put(unauthorised_user.client, entry.id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    @pytest.mark.requires_actions("delete")
    def test_delete_success(self, session: Session, authorised_user: FixtureUser) -> None:
        """Test that authorised users can successfully delete existing items."""
        entry = self.create_entry(session, authorised_user)
        response = self.delete(authorised_user.client, entry.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.requires_actions("delete")
    def test_delete_non_exist(self, authorised_user: FixtureUser) -> None:
        """Test that DELETE requests for non-existent items return a 404 error."""
        response = self.delete(authorised_user.client, 0)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.requires_actions("delete")
    def test_delete_unauthenticated(self, session: Session, client: TestClient, authorised_user: FixtureUser) -> None:
        """Test that unauthenticated requests to delete items are rejected."""
        entry = self.create_entry(session, authorised_user)
        response = self.delete(client, entry.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.requires_actions("delete")
    def test_delete_forbidden(
        self, session: Session, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """Test that users are denied access to delete items they don't have permission to remove."""
        entry = self.create_entry(session, authorised_user)
        response = self.delete(unauthorised_user.client, entry.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN


def _expected_status(undefined_action: str, defined_actions: set[str]) -> int:
    """Return 405 if the path is already registered by another action, else 404."""

    collection_actions = {"GET_ALL", "POST"}
    item_actions = {"GET_ONE", "PUT", "DELETE"}

    if undefined_action in collection_actions:
        path_exists = bool(defined_actions & collection_actions)
    else:
        path_exists = bool(defined_actions & item_actions)

    return status.HTTP_405_METHOD_NOT_ALLOWED if path_exists else status.HTTP_404_NOT_FOUND


_ACTION_META = {
    "GET_ALL": ("GET", "/"),
    "POST": ("POST", "/"),
    "GET_ONE": ("GET", "/1"),
    "PUT": ("PUT", "/1"),
    "DELETE": ("DELETE", "/1"),
}


def make_undefined_method_params(defined: list[str], undefined: list[str]):
    """Generate pytest.param objects for undefined methods."""
    defined_upper = {a.upper() for a in defined}
    params = []
    for action in undefined:
        action = action.upper()
        http_method, path_suffix = _ACTION_META[action]
        expected = _expected_status(action, defined_upper)
        params.append(pytest.param(http_method, path_suffix, expected, id=f"{action}_expects_{expected}"))
    return params
