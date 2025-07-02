"""
This module is designed to facilitate testing and database interaction in the application. It includes utility functions,
fixtures, and configurations for setting up and managing the SQLAlchemy database, test users, test tokens, and mock
clients for API testing. The provided components streamline testing by enabling convenient access to preconfigured
resources.

Key Components:
----------------
- **SQLALCHEMY_DATABASE_URL**: Configuration for the database connection URL.
- **engine**: SQLAlchemy engine used to manage connections and interact with the database.
- **TestingSessionLocal**: A SQLAlchemy session factory designed specifically for testing purposes.
- **session**: A fixture to provide a database session for tests.
- **client**: A fixture to provide an API test client.
- **create_user**: Utility function for creating test users in the database.
- **test_user1** and **test_user2**: Fixtures for pre-configured test users.
- **token1** and **token2**: Fixtures for generating authentication tokens for the pre-configured test users.
- **authorized_client** and **authorized_client2**: Fixtures to provide authenticated API clients for the test users.
- **test_jobs**: Fixture for creating and managing test jobs in the application.

This module is instrumental for efficiently executing unit and integration tests by establishing a robust test environment
and providing the necessary utilities for seamless interactions with the application's data and APIs.
"""

import datetime as dt
from typing import Any, Generator

import pytest
from fastapi import status
from requests import Response
from sqlalchemy import create_engine, orm
from starlette.testclient import TestClient

from app import models, database, schemas
from app.main import app
from app.oauth2 import create_access_token
from tests.utils.create_data import (
    create_users,
    create_companies,
    create_locations,
    create_aggregators,
    create_keywords,
    create_people,
    create_jobs,
    create_files,
    create_job_applications,
    create_interviews,
)

SQLALCHEMY_DATABASE_URL = database.SQLALCHEMY_DATABASE_URL + "_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def session() -> Generator[orm.Session, Any, None]:
    """Fixture that sets up and tears down a new database session for each test function.
    This fixture creates a fresh database session by creating and dropping all tables in the
    test database. It yields a session that can be used by test functions. After the test
    function completes, the session is closed.
    :yield: A new SQLAlchemy session bound to the test database."""

    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session) -> Generator[TestClient, Any, None]:
    """Fixture that provides a test client with an overridden database dependency.
    This fixture creates a test client by overriding the default database dependency
    to use the test database session. It yields the TestClient, allowing the test
    functions to make requests to the FastAPI application.
    :param session: The database session fixture to override the database dependency.
    :yield: The FastAPI TestClient with the overridden database dependency."""

    def override_get_db() -> Generator[orm.Session, Any, None]:
        """Override the default database dependency to use the test database session."""
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)  # Clean up dependency override


@pytest.fixture
def test_users(session):
    """Create test user data"""

    return create_users(session)


@pytest.fixture
def tokens(test_users) -> list[str]:
    """Fixture that generates access tokens for the given test users."""

    return [create_access_token({"user_id": user.id}) for user in test_users]


@pytest.fixture
def authorised_clients(
    client: TestClient,
    tokens: list[str],
) -> list[TestClient]:
    """Fixture that provides a list of authenticated test clients."""

    clients = []
    for token in tokens:
        authorized_client = TestClient(client.app)
        authorized_client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
        clients.append(authorized_client)
    return clients


@pytest.fixture
def test_locations(session, test_users):
    """Create test location data"""

    return create_locations(session)


@pytest.fixture
def test_companies(session, test_users):
    """Create test company data"""

    return create_companies(session)


@pytest.fixture
def test_persons(session, test_users, test_companies):
    """Create test person data"""

    return create_people(session)


@pytest.fixture
def test_aggregators(session, test_users):
    """Create test aggregator data"""

    return create_aggregators(session)


@pytest.fixture
def test_keywords(session, test_users):
    """Create test keyword data"""

    return create_keywords(session)


@pytest.fixture
def test_files(session, test_users):
    """Create test files for job applications"""

    return create_files(session)


@pytest.fixture
def test_jobs(session, test_users, test_companies, test_locations, test_keywords, test_persons):
    """Create test job data"""

    return create_jobs(session, test_keywords, test_persons)


@pytest.fixture
def test_job_applications(session, test_users, test_jobs, test_files):
    """Create test job application data using File references"""

    return create_job_applications(session)


@pytest.fixture
def test_interviews(session, test_users, test_job_applications, test_locations, test_persons):
    """Create test interview data"""

    return create_interviews(session, test_persons)


class CRUDTestBase:
    """Base class for CRUD tests on FastAPI routes.

    Subclasses must override:
    - endpoint: str - base URL path for the resource (e.g. "/aggregators")
    - schema: Pydantic model class for input validation (e.g. schemas.Aggregator)
    - out_schema: Pydantic model class for output validation (e.g. schemas.AggregatorOut)
    - test_data_fixture: str - name of pytest fixture providing list of test objects"""

    endpoint: str = ""
    schema = None
    out_schema = None
    test_data: str = ""
    update_data: dict = None
    create_data: list[dict] = None
    add_fixture = None

    def check_output(
        self,
        test_data: list[schemas.BaseModel] | list[dict] | dict | schemas.BaseModel,
        response_data: list[dict] | dict,
    ):
        """Check that the output of a test matches the test data.
        :param test_data: The test data to compare against.
        :param response_data: The output data to compare against."""

        if isinstance(test_data, list) and isinstance(response_data, list):
            for d1, d2 in zip(test_data, response_data):
                return self.check_output(d1, d2)

        # Process the response
        if isinstance(response_data, dict):
            response_data = self.out_schema(**response_data)

        # # Process the input
        # if isinstance(test_data, dict):
        #     test_data = self.schema(**test_data)

        if isinstance(test_data, dict):
            items = test_data.items()
        else:
            items = vars(test_data).items()

        for key, value in items:
            if key[0] != "_":
                response_value = getattr(response_data, key)
                if isinstance(value, models.Base) or isinstance(value, list):
                    self.check_output(value, response_value)
                elif key == "date" and isinstance(value, str):
                    # Handle datetime string comparison using fromisoformat
                    if isinstance(response_value, dt.datetime):
                        # Parse the string datetime and compare
                        parsed_value = dt.datetime.fromisoformat(value)
                        # Handle timezone differences - normalize both to the same timezone state
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

    # ------------------------------------------------- HELPER METHODS -------------------------------------------------

    def get_all(self, client) -> Response:
        """Helper method to get all items from the endpoint."""

        return client.get(self.endpoint)

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

    @pytest.fixture(autouse=True)
    def setup_method(self, request) -> None:
        """Fixture that runs before each test method."""

        if isinstance(self.add_fixture, list):
            for fixture in self.add_fixture:
                request.getfixturevalue(fixture)

    # ------------------------------------------------------- GET ------------------------------------------------------

    def test_get_all_success(
        self,
        authorised_clients,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_all(authorised_clients[0])
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_data, response.json())

    def test_get_all_unauthorized(
        self,
        client: TestClient,
    ) -> None:
        response = self.get_all(client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_one_success(
        self,
        authorised_clients,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(authorised_clients[0], test_data[0].id)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_data[0], response.json())

    def test_get_one_unauthorized(
        self,
        client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_one_other_user(
        self,
        authorised_clients,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(authorised_clients[1], test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_one_non_exist(
        self,
        authorised_clients,
    ) -> None:
        response = self.get_one(authorised_clients[0], 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_post_success(
        self,
        authorised_clients,
    ) -> None:
        """
        Generic POST test using class attribute post_test_data.
        Subclasses should set post_test_data = [dict(...), ...]
        """

        for create_data in self.create_data:
            create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
            response = self.post(authorised_clients[0], create_data)
            assert response.status_code == status.HTTP_201_CREATED
            self.check_output(create_data, response.json())

    def test_post_unauthorized(
        self,
        client,
    ) -> None:
        response = self.post(client, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ------------------------------------------------------- PUT ------------------------------------------------------

    def test_put_success(
        self,
        authorised_clients,
        request,
    ) -> None:
        request.getfixturevalue(self.test_data)
        response = self.put(authorised_clients[0], self.update_data["id"], self.update_data)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(self.update_data, response.json())

    def test_put_empty_body(self, authorised_clients, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(authorised_clients[0], test_data[0].id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_put_non_exist(self, authorised_clients) -> None:
        response = self.put(authorised_clients[0], 999999, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_unauthorized(self, client, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_other_user(self, authorised_clients, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(authorised_clients[1], test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    def test_delete_success(self, authorised_clients, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(authorised_clients[0], test_data[0].id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_exist(self, authorised_clients) -> None:
        response = self.delete(authorised_clients[0], 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthorized(self, client, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_other_user(self, authorised_clients, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(authorised_clients[1], test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
