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

from test.data import (
    COMPANIES_DATA,
    LOCATIONS_DATA,
    PERSONS_DATA,
    AGGREGATORS_DATA,
    KEYWORDS_DATA,
    FILES_DATA,
    JOBS_DATA,
    JOB_APPLICATIONS_DATA,
    INTERVIEWS_DATA,
    JOB_KEYWORD_MAPPINGS,
    JOB_CONTACT_MAPPINGS,
    INTERVIEW_INTERVIEWER_MAPPINGS,
    add_mappings,
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
def test_user2(client: TestClient, test_user1) -> dict:
    """Second test user. Test user 1 is called to get it created first"""

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
def test_locations(session, test_user1, test_user2):
    """Create test location data"""

    locations = [models.Location(**location) for location in LOCATIONS_DATA]
    session.add_all(locations)
    session.commit()
    locations = session.query(models.Location).all()
    return locations


@pytest.fixture
def test_companies(session, test_user1, test_user2):
    """Create test company data"""

    companies = [models.Company(**company) for company in COMPANIES_DATA]
    session.add_all(companies)
    session.commit()
    companies = session.query(models.Company).all()
    return companies


@pytest.fixture
def test_persons(session, test_user1, test_user2, test_companies):
    """Create test person data"""

    persons = [models.Person(**person) for person in PERSONS_DATA]
    session.add_all(persons)
    session.commit()
    persons = session.query(models.Person).all()
    return persons


@pytest.fixture
def test_aggregators(session, test_user1, test_user2):
    """Create test aggregator data"""

    aggregators = [models.Aggregator(**aggregator) for aggregator in AGGREGATORS_DATA]
    session.add_all(aggregators)
    session.commit()
    aggregators = session.query(models.Aggregator).all()
    return aggregators


@pytest.fixture
def test_keywords(session, test_user1, test_user2):
    """Create test keyword data"""

    keywords = [models.Keyword(**keyword) for keyword in KEYWORDS_DATA]
    session.add_all(keywords)
    session.commit()
    keywords = session.query(models.Keyword).all()
    return keywords


@pytest.fixture
def test_files(session, test_user1, test_user2):
    """Create test files for job applications"""

    files = [models.File(**file) for file in FILES_DATA]
    session.add_all(files)
    session.commit()
    files = session.query(models.File).all()
    return files


@pytest.fixture
def test_jobs(session, test_user1, test_user2, test_companies, test_locations, test_keywords, test_persons):
    """Create test job data"""

    jobs = [models.Job(**job) for job in JOBS_DATA]
    session.add_all(jobs)
    session.commit()
    jobs = session.query(models.Job).all()

    # Add keywords to jobs
    add_mappings(
        primary_data=jobs,
        secondary_data=test_keywords,
        mapping_data=JOB_KEYWORD_MAPPINGS,
        primary_key="job_id",
        secondary_key="keyword_ids",
        relationship_attr="keywords",
    )

    # Add contacts to jobs
    add_mappings(
        primary_data=jobs,
        secondary_data=test_persons,
        mapping_data=JOB_CONTACT_MAPPINGS,
        primary_key="job_id",
        secondary_key="person_ids",
        relationship_attr="contacts",
    )

    session.commit()
    jobs = session.query(models.Job).all()
    return jobs


@pytest.fixture
def test_job_applications(session, test_user1, test_user2, test_jobs, test_files):
    """Create test job application data using File references"""

    job_applications = [models.JobApplication(**job_application) for job_application in JOB_APPLICATIONS_DATA]
    session.add_all(job_applications)
    session.commit()
    job_applications = session.query(models.JobApplication).all()
    return job_applications


@pytest.fixture
def test_interviews(session, test_user1, test_user2, test_job_applications, test_locations, test_persons):
    """Create test interview data"""

    interviews = [models.Interview(**interview) for interview in INTERVIEWS_DATA]
    session.add_all(interviews)
    session.commit()
    interviews = session.query(models.Interview).all()

    # Add interviewers to interviews
    add_mappings(
        primary_data=interviews,
        secondary_data=test_persons,
        mapping_data=INTERVIEW_INTERVIEWER_MAPPINGS,
        primary_key="interview_id",
        secondary_key="person_ids",
        relationship_attr="interviewers",
    )

    session.commit()
    return interviews


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
    update_data: list[dict] = None
    create_data: dict = None
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
        authorized_client1,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_all(authorized_client1)
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
        authorized_client1,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(authorized_client1, test_data[0].id)
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
        authorized_client2,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(authorized_client2, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_one_non_exist(
        self,
        authorized_client1,
    ) -> None:
        response = self.get_one(authorized_client1, 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_post_success(
        self,
        authorized_client1,
    ) -> None:
        """
        Generic POST test using class attribute post_test_data.
        Subclasses should set post_test_data = [dict(...), ...]
        """
        for create_data in self.create_data:
            create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
            response = self.post(authorized_client1, create_data)
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
        authorized_client1,
        request,
    ) -> None:
        request.getfixturevalue(self.test_data)
        response = self.put(authorized_client1, self.update_data["id"], self.update_data)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(self.update_data, response.json())

    def test_put_empty_body(self, authorized_client1, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(authorized_client1, test_data[0].id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_put_non_exist(self, authorized_client1) -> None:
        response = self.put(authorized_client1, 999999, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_unauthorized(self, client, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_other_user(self, authorized_client2, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(authorized_client2, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    def test_delete_success(self, authorized_client1, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(authorized_client1, test_data[0].id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_exist(self, authorized_client1) -> None:
        response = self.delete(authorized_client1, 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthorized(self, client, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_other_user(self, authorized_client2, request) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(authorized_client2, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
