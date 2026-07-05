"""
Test configuration and pytest hooks.

Fixtures are organised in the tests/fixtures/ directory:
- database.py: Database session and engine fixtures
- clients.py: API test client fixtures
- users.py: User-related fixtures
- test_data.py: Test data fixtures for various models

The CRUDTestBase class is in tests/utils/crud_test_base.py
"""

import datetime as dt
import os
from typing import Any, Type
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel
from requests import Response
from starlette import status
from starlette.testclient import TestClient

from app import models
from tests.base_test import BaseTest
from tests.utils.test_data.geolocation import MOCK_GEOCODING_RESPONSES

# Load fixtures from separate modules
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.clients",
    "tests.fixtures.users",
    "tests.fixtures.test_data",
    "tests.fixtures.job_scraping",
    "tests.fixtures.job_rating",
    "tests.fixtures.provider_monitoring",
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


@pytest.fixture(autouse=True)
def block_real_apify_client():
    """Safety net: no test may construct a real ApifyClient, which would hit the live Apify API.
    Tests that exercise Apify scrapers patch ApifyClient themselves; this makes an un-mocked
    construction fail loudly instead of reaching the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real ApifyClient constructed in a test - patch "
            "'app.job_email_scraping.job_scrapers.apify.ApifyClient' in your test or fixture."
        )

    with patch("app.job_email_scraping.job_scrapers.apify.ApifyClient", side_effect=fail):
        yield


@pytest.fixture(autouse=True)
def block_real_brightdata_requests():
    """Safety net: no test may make a real BrightData HTTP request, which would hit the live API.
    Tests that exercise BrightData scrapers patch the scraper's `requests` themselves; this makes an
    un-mocked request fail loudly instead of reaching the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real BrightData HTTP request in a test - patch "
            "'app.job_email_scraping.job_scrapers.brightdata.requests' in your test or fixture."
        )

    mock_requests = MagicMock()
    mock_requests.get.side_effect = fail
    mock_requests.post.side_effect = fail
    with patch("app.job_email_scraping.job_scrapers.brightdata.requests", mock_requests):
        yield


@pytest.fixture(autouse=True)
def block_real_openai_client():
    """Safety net: no test may reach the live OpenAI API. Tests that exercise job rating patch the
    client themselves; this makes an un-mocked chat completion fail loudly instead of hitting the network.

    Guards both the already-constructed module-level client and the ``OpenAI`` class itself, so any
    client built during a test (now or in future code paths) is also a loud mock."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real OpenAI request in a test - patch 'app.job_rating.chatgpt.client' in your test or fixture."
        )

    def make_loud_client(*_args, **_kwargs):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fail
        return mock_client

    with (
        patch("app.job_rating.chatgpt.client", make_loud_client()),
        patch("openai.OpenAI", side_effect=make_loud_client),
    ):
        yield


@pytest.fixture(autouse=True)
def block_real_anthropic_client():
    """Safety net: no test may reach the live Anthropic API. Tests that exercise job rating patch the
    client themselves; this makes an un-mocked message create fail loudly instead of hitting the network.

    Guards both the already-constructed module-level client and the ``Anthropic`` class itself, so any
    client built during a test (now or in future code paths) is also a loud mock."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real Anthropic request in a test - patch 'app.job_rating.claude.client' in your test or fixture."
        )

    def make_loud_client(*_args, **_kwargs):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = fail
        return mock_client

    with (
        patch("app.job_rating.claude.client", make_loud_client()),
        patch("anthropic.Anthropic", side_effect=make_loud_client),
    ):
        yield


@pytest.fixture(autouse=True)
def block_real_provider_http():
    """Safety net for provider-monitoring fetchers (Anthropic cost_report, Apify, BrightData, Stripe),
    which all reach the network through `request_with_retry` -> `requests.request` in app.utilities.http.
    Tests patch `request_with_retry` in each fetch module; this blocks the transport underneath so any
    un-mocked fetch fails loudly instead of hitting the live provider API."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real provider HTTP request in a test - patch 'request_with_retry' in the relevant "
            "app.provider_monitoring.*.fetch module in your test or fixture."
        )

    mock_requests = MagicMock()
    mock_requests.request.side_effect = fail
    with patch("app.utilities.http.requests", mock_requests):
        yield


@pytest.fixture(autouse=True)
def block_real_stripe_requests():
    """Safety net: no test may reach the live Stripe API through the SDK. The payments code calls the
    Stripe SDK directly (e.g. `stripe.Customer.create_async`), and every typed call funnels through
    `_APIRequestor.request`/`request_async`. Tests patch the specific SDK method they exercise; this
    blocks the transport underneath so any un-mocked call fails loudly instead of hitting the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real Stripe request in a test - patch the specific 'stripe.*' SDK call "
            "(e.g. 'app.payments.customer.stripe.Customer.retrieve_async') in your test or fixture."
        )

    with (
        patch("stripe._api_requestor._APIRequestor.request", side_effect=fail),
        patch("stripe._api_requestor._APIRequestor.request_async", side_effect=fail),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_nominatim_get():
    """Auto-mock Nominatim HTTP calls using MOCK_GEOCODING_RESPONSES.
    Known queries return a real-shaped Nominatim response; unknown queries return []
    which causes call_geocoding_api to raise ValueError."""

    def side_effect(url, **kwargs):
        """Mock the requests.get call to Nominatim."""
        _ = url
        params = kwargs.get("params", {})
        query = params.get("q")
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = MOCK_GEOCODING_RESPONSES.get(query, [])
        return mock_response

    with (
        patch("app.geolocation.geolocation.requests.get", side_effect=side_effect) as mock,
        patch("app.geolocation.geolocation.time.sleep"),
    ):
        yield mock


@pytest.fixture
def mock_email_verif():
    """Patch the email-change verification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_change_verification") as mock:
        yield mock


@pytest.fixture
def mock_password_notify():
    """Patch the password-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.user.email_service.send_password_changed_notification") as mock:
        yield mock


@pytest.fixture
def mock_email_notify():
    """Patch the email-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_change_notification") as mock:
        yield mock


@pytest.fixture
def mock_release_email():
    """Patch the new-version release email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.user.email_service.send_new_version_email") as mock:
        yield mock


@pytest.fixture
def mock_verification_email():
    """Patch the email-verification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_email_verification_email") as mock:
        yield mock


@pytest.fixture
def mock_password_reset_email():
    """Patch the password-reset-request email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_password_reset_email") as mock:
        yield mock


@pytest.fixture
def mock_password_changed_email():
    """Patch the password-changed notification email so tests can spy on it (not autouse - opt in by name).
    Real emails are never sent in tests anyway (send_email no-ops under test_mode); this is for assertions."""

    with patch("app.core.routers.auth.email_service.send_password_changed_notification") as mock:
        yield mock


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


class CRUDTestBase(BaseTest):
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
    - actions_to_test: list[str] - which CRUD actions to test (any subset of ["get", "post", "put", "delete"])"""

    endpoint: str = ""
    create_schema: Type[BaseModel] | None = None
    out_schema: Type[BaseModel] | None = None
    test_data_ref: str = ""
    update_data: dict[str, str | int] = None
    create_data: list[dict] = None
    required_fixture: str = None
    get_unauthorised_fixture: str = None
    unauthorised_data_fixture = None
    admin_only: bool = False
    actions_to_test: list[str] = ["get", "post", "put", "delete"]
    too_long_create_data: dict | None = None

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

        if isinstance(response_data, dict) and self.out_schema is not None:
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

    @pytest.fixture
    def authorised_user(self, test_regular_user, test_admin_user) -> models.User:
        """The user whose client is used for authorised requests (admin for admin_only endpoints)."""
        return test_admin_user if self.admin_only else test_regular_user

    @pytest.fixture
    def unauthorised_user(self, test_regular_user, test_admin_user) -> models.User:
        """The user whose client should be denied access (the opposite of authorised_user)."""
        return test_regular_user if self.admin_only else test_admin_user

    def get_user_data(self, user, data: list) -> list:
        """Get create_data filtered by owner_id based on admin_only setting."""
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
    def test_data(self, request, authorised_user) -> list:
        """Fixture to get the test data from the specified fixture name."""
        return self.get_user_data(authorised_user, request.getfixturevalue(self.test_data_ref))

    # ----------------------------------------------------- GET ALL ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_authorised(self, test_data, authorised_user) -> None:
        """Test that authorised users can successfully retrieve all items from the endpoint."""
        client = authorised_user.client
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
    def test_get_all_non_admin(self, test_data, unauthorised_user) -> None:
        """Test that non-admin users requests to get all items are rejected for admin_only endpoints."""
        if self.admin_only:
            client = unauthorised_user.client
            response = self.get_all(client)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_all")
    def test_get_all_data_only_authorised(self, request, test_regular_user) -> None:
        """Test that users only see data they own when retrieving all items (non-admin endpoints only)."""
        if not self.admin_only and self.get_unauthorised_fixture:
            owner_id = request.getfixturevalue(self.get_unauthorised_fixture)[1]
            response = self.get_all(test_regular_user.client)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            print(data)
            if data:
                assert_ownership(data, owner_id)

    # ----------------------------------------------------- GET ONE ----------------------------------------------------

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_success(self, test_data, authorised_user) -> None:
        """Test that authorised users can successfully retrieve a specific item by ID."""
        client = authorised_user.client
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
    def test_get_one_incorrect_user(self, test_data, unauthorised_user) -> None:
        """Test that users are denied access to items they don't have permission to view."""
        client = unauthorised_user.client
        response = self.get_one(client, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("get", "get_one")
    def test_get_one_non_exist(self, authorised_user) -> None:
        """Test that requests for non-existent items return a 404 error."""
        client = authorised_user.client
        response = self.get_one(client, 0)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    @pytest.mark.requires_actions("post")
    def test_post_success(self, authorised_user) -> None:
        """Test that authorised users can successfully create new items."""
        client = authorised_user.client
        for create_data in self.get_user_data(authorised_user, self.create_data):
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
    def test_post_non_admin(self, authorised_user, unauthorised_user) -> None:
        """Test that non-admin users are denied access to create items on admin-only endpoints."""
        if self.admin_only:
            client = unauthorised_user.client
            for create_data in self.get_user_data(authorised_user, self.create_data):
                create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
                response = self.post(client, create_data)
                assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.requires_actions("post")
    def test_post_field_too_long(self, authorised_user) -> None:
        """Test that creating an item with a field exceeding its max length returns 422."""
        if self.too_long_create_data is None:
            return
        client = authorised_user.client
        response = self.post(client, self.too_long_create_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.requires_actions("post")
    def test_post_unowned_link_rejected(self, request, test_regular_user) -> None:
        """Test that creating an entry linking to a related entry the user does not own is rejected (non-admin endpoints)."""
        if not self.admin_only and self.unauthorised_data_fixture:
            data, owner_id = request.getfixturevalue(self.unauthorised_data_fixture)[:2]
            for datum in data:
                datum = {key: value for key, value in datum.items() if key not in ("id", "owner_id")}
                response = self.post(test_regular_user.client, datum)
                assert response.status_code == status.HTTP_403_FORBIDDEN

    # ------------------------------------------------------- PUT ------------------------------------------------------

    @pytest.mark.requires_actions("put")
    def test_put_success(self, test_data, authorised_user) -> None:
        """Test that authorised users can successfully update existing items."""
        client = authorised_user.client
        data_id = self.update_data.get("id")
        assert isinstance(data_id, int)
        response = self.put(client, data_id, self.update_data)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(self.update_data, response.json())

    @pytest.mark.requires_actions("put")
    def test_put_empty_body(self, test_data, authorised_user) -> None:
        """Test that PUT requests with empty request bodies are rejected."""
        client = authorised_user.client
        response = self.put(client, test_data[0].id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.requires_actions("put")
    def test_put_non_exist(self, authorised_user) -> None:
        """Test that PUT requests for non-existent items return a 404 error."""
        client = authorised_user.client
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
    def test_put_forbidden(self, test_data, unauthorised_user) -> None:
        """Test that users are denied access to update items they don't have permission to modify."""
        client = unauthorised_user.client
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    @pytest.mark.requires_actions("delete")
    def test_delete_success(self, test_data, authorised_user) -> None:
        """Test that authorised users can successfully delete existing items."""
        client = authorised_user.client
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.requires_actions("delete")
    def test_delete_non_exist(self, authorised_user) -> None:
        """Test that DELETE requests for non-existent items return a 404 error."""
        client = authorised_user.client
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
    def test_delete_forbidden(self, test_data, unauthorised_user) -> None:
        """Test that users are denied access to delete items they don't have permission to remove."""
        client = unauthorised_user.client
        response = self.delete(client, test_data[0].id)
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
