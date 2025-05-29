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

from typing import Any, Generator

import pytest
from sqlalchemy import create_engine, orm
from starlette.testclient import TestClient

from app import database, models
from app.main import app
from app.oauth2 import create_access_token

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


def create_user(client: TestClient, **user_data) -> dict:
    """Helper function to create a new user via the FastAPI application.
    This function sends a POST request to the "/users/" endpoint with the provided
    user data to create a new user. It asserts that the response status code is 201
    (created), and it returns the newly created user data, including the password.
    :param client: The FastAPI TestClient to make the request.
    :param user_data: A dictionary of user attributes (e.g., email, password, username).
    :return: The created user data, including the password."""

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user1(client: TestClient) -> dict:
    """First test user"""
    user_data = {
        "email": "user1@email.com",
        "password": "user1_password",
        "username": "user1",
    }
    return create_user(client, **user_data)


@pytest.fixture
def test_user2(client: TestClient) -> dict:
    """Second test user"""

    user_data = {
        "email": "user2@email.com",
        "password": "user2_password",
        "username": "user2",
    }
    return create_user(client, **user_data)


@pytest.fixture
def token1(test_user1: dict) -> str:
    """Fixture that generates an access token for the given test user.
    This fixture uses the `create_access_token` function to generate a JWT token
    for the provided test user, which is then used for authorization in test requests.
    :param test_user1: The test user for whom to generate the access token.
    :return: The generated JWT access token."""

    return create_access_token({"user_id": test_user1["id"]})


@pytest.fixture
def token2(test_user2: dict) -> str:
    """Fixture that generates an access token for the given test user.
    This fixture uses the `create_access_token` function to generate a JWT token
    for the provided test user, which is then used for authorization in test requests.
    :param test_user2: The test user for whom to generate the access token.
    :return: The generated JWT access token."""

    return create_access_token({"user_id": test_user2["id"]})


@pytest.fixture
def authorized_client1(
    client: TestClient,
    token1: str,
) -> TestClient:
    """Fixture that provides a test client with authorization headers.
    This fixture adds the generated JWT token to the headers of the FastAPI TestClient
    to simulate an authorized request, allowing the client to make requests as the
    authenticated user.
    :param client: The FastAPI TestClient to make the request.
    :param token1: The JWT token to add to the Authorization header.
    :return: The FastAPI TestClient with the Authorization header set."""

    client.headers = {**client.headers, "Authorization": f"Bearer {token1}"}
    return client


@pytest.fixture
def authorized_client2(
    client: TestClient,
    token2: str,
) -> TestClient:
    """Fixture that provides a test client with authorization headers.
    This fixture adds the generated JWT token to the headers of the FastAPI TestClient
    to simulate an authorized request, allowing the client to make requests as the
    authenticated user.
    :param client: The FastAPI TestClient to make the request.
    :param token2: The JWT token to add to the Authorization header.
    :return: The FastAPI TestClient with the Authorization header set."""

    client.headers = {**client.headers, "Authorization": f"Bearer {token2}"}
    return client


@pytest.fixture
def test_jobs(
    test_user1: dict,
    test_user2: dict,
    session: orm.Session,
):
    """Fixture that creates and returns a list of test jobs.
    This fixture creates several jobs in the test database for two users. It adds
    the jobs to the database and commits the transaction. It then returns the list
    of all jobs from the database.
    :param test_user1: The first test user who owns some of the jobs.
    :param test_user2: The second test user who owns other jobs.
    :param session: The SQLAlchemy session to interact with the database.
    :return: A list of all jobs created for the test users."""

    data = [
        {"title": "1st title", "content": "1st content", "owner_id": test_user1["id"]},
        {"title": "2nd title", "content": "2nd content", "owner_id": test_user1["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": test_user1["id"]},
        {"title": "1st title", "content": "1st content", "owner_id": test_user2["id"]},
    ]

    jobs = [models.Job(**job) for job in data]
    session.add_all(jobs)
    session.commit()
    jobs = session.query(models.Job).all()
    return jobs


@pytest.fixture
def test_locations(
    test_user1: dict,
    test_user2: dict,
    session: orm.Session,
):
    """Fixture that creates and returns a list of test locations.
    This fixture creates several locations in the test database for two users. It adds
    the locations to the database and commits the transaction. It then returns the list
    of all locations from the database.
    :param test_user1: The first test user who owns some of the locations.
    :param test_user2: The second test user who owns other locations.
    :param session: The SQLAlchemy session to interact with the database.
    :return: A list of all locations created for the test users."""

    data = [
        {"postcode": "OX5 1HN", "owner_id": test_user1["id"]},
        {"city": "Oxford", "owner_id": test_user1["id"]},
        {"country": "UK", "owner_id": test_user1["id"]},
        {"remote": True, "owner_id": test_user2["id"]},
        {"postcode": "OX5 1HN", "owner_id": test_user1["id"], "country": "UK"},
    ]

    locations = [models.Location(**location) for location in data]
    session.add_all(locations)
    session.commit()
    locations = session.query(models.Location).all()
    return locations


def compare(location_queried, location_obtained):

    if isinstance(location_queried, list):
        for loc1, loc2 in zip(location_queried, location_obtained):
            compare(loc1, loc2)
    elif isinstance(location_queried, dict):
        for key, value in location_queried.items():
            assert getattr(location_obtained, key) == value
    else:
        for key, value in vars(location_queried).items():
            assert value == getattr(location_obtained, key)
