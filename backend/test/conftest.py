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
def test_locations(session, test_user1, test_user2):
    """Create test location data"""
    locations = [
        models.Location(postcode="10001", city="New York", country="USA", remote=False, owner_id=test_user1["id"]),
        models.Location(postcode="90210", city="Beverly Hills", country="USA", remote=False, owner_id=test_user1["id"]),
        models.Location(postcode="SW1A 1AA", city="London", country="UK", remote=False, owner_id=test_user2["id"]),
        models.Location(city="San Francisco", country="USA", remote=True, owner_id=test_user1["id"]),
        models.Location(country="Germany", remote=True, owner_id=test_user2["id"]),
    ]

    session.add_all(locations)
    session.commit()
    locations = session.query(models.Location).all()
    return locations


@pytest.fixture
def test_companies(session, test_user1, test_user2):
    """Create test company data"""

    companies = [
        models.Company(
            name="Tech Corp",
            description="A leading technology company specializing in software development",
            url="https://techcorp.com",
            owner_id=test_user1["id"],
        ),
        models.Company(
            name="Data Systems Inc",
            description="Enterprise data solutions and analytics",
            url="https://datasystems.com",
            owner_id=test_user1["id"],
        ),
        models.Company(
            name="Cloud Solutions Ltd",
            description="Cloud infrastructure and services provider",
            url="https://cloudsolutions.co.uk",
            owner_id=test_user2["id"],
        ),
        models.Company(
            name="StartupXYZ",
            description="Innovative fintech startup",
            url="https://startupxyz.io",
            owner_id=test_user1["id"],
        ),
        models.Company(
            name="Enterprise Corp",
            description="Large enterprise software solutions",
            owner_id=test_user2["id"],
        ),
    ]

    session.add_all(companies)
    session.commit()
    companies = session.query(models.Company).all()
    return companies


@pytest.fixture
def test_persons(session, test_user1, test_user2, test_companies):
    """Create test person data"""

    persons = [
        models.Person(
            first_name="John",
            last_name="Smith",
            email="john.smith@techcorp.com",
            phone="+1-555-0123",
            linkedin_url="https://linkedin.com/in/johnsmith",
            company_id=test_companies[0].id,
            owner_id=test_user1["id"],
        ),
        models.Person(
            first_name="Sarah",
            last_name="Johnson",
            email="sarah.johnson@datasystems.com",
            phone="+1-555-0456",
            linkedin_url="https://linkedin.com/in/sarahjohnson",
            company_id=test_companies[1].id,
            owner_id=test_user1["id"],
        ),
        models.Person(
            first_name="Michael",
            last_name="Brown",
            email="m.brown@cloudsolutions.co.uk",
            phone="+44-20-7946-0958",
            linkedin_url="https://linkedin.com/in/michaelbrown",
            company_id=test_companies[2].id,
            owner_id=test_user2["id"],
        ),
        models.Person(
            first_name="Emma",
            last_name="Davis",
            email="emma@startupxyz.io",
            phone="+1-555-0789",
            company_id=test_companies[3].id,
            owner_id=test_user1["id"],
        ),
        models.Person(
            first_name="David",
            last_name="Wilson",
            linkedin_url="https://linkedin.com/in/davidwilson",
            company_id=test_companies[4].id,
            owner_id=test_user2["id"],
        ),
    ]

    session.add_all(persons)
    session.commit()
    persons = session.query(models.Person).all()
    return persons


@pytest.fixture
def test_aggregators(session, test_user1, test_user2):
    """Create test aggregator data"""

    aggregators = [
        models.Aggregator(name="LinkedIn Jobs", url="https://linkedin.com/jobs", owner_id=test_user1["id"]),
        models.Aggregator(name="Indeed", url="https://indeed.com", owner_id=test_user1["id"]),
        models.Aggregator(name="Glassdoor", url="https://glassdoor.com", owner_id=test_user2["id"]),
        models.Aggregator(name="Stack Overflow Jobs", url="https://stackoverflow.com/jobs", owner_id=test_user1["id"]),
        models.Aggregator(name="AngelList", url="https://angel.co", owner_id=test_user2["id"]),
    ]

    session.add_all(aggregators)
    session.commit()
    aggregators = session.query(models.Aggregator).all()
    return aggregators


@pytest.fixture
def test_keywords(session, test_user1, test_user2):
    """Create test keyword data"""
    keywords = [
        models.Keyword(name="Python", owner_id=test_user1["id"]),
        models.Keyword(name="JavaScript", owner_id=test_user1["id"]),
        models.Keyword(name="React", owner_id=test_user1["id"]),
        models.Keyword(name="Node.js", owner_id=test_user1["id"]),
        models.Keyword(name="Machine Learning", owner_id=test_user2["id"]),
        models.Keyword(name="AWS", owner_id=test_user1["id"]),
        models.Keyword(name="Docker", owner_id=test_user2["id"]),
        models.Keyword(name="Kubernetes", owner_id=test_user1["id"]),
        models.Keyword(name="SQL", owner_id=test_user2["id"]),
        models.Keyword(name="FastAPI", owner_id=test_user1["id"]),
    ]
    session.add_all(keywords)
    session.commit()
    keywords = session.query(models.Keyword).all()
    return keywords


@pytest.fixture
def test_jobs(session, test_user1, test_user2, test_companies, test_locations, test_keywords):
    """Create test job data"""

    jobs = [
        models.Job(
            title="Senior Python Developer",
            description="Looking for an experienced Python developer to join our backend team",
            salary_min=80000,
            salary_max=120000,
            personal_rating=8,
            url="https://techcorp.com/careers/senior-python-dev",
            company_id=test_companies[0].id,
            location_id=test_locations[0].id,
            note="Great company culture, flexible hours",
            owner_id=test_user1["id"],
        ),
        models.Job(
            title="Frontend React Developer",
            description="Join our frontend team building modern web applications",
            salary_min=70000,
            salary_max=100000,
            personal_rating=7,
            url="https://datasystems.com/jobs/react-dev",
            company_id=test_companies[1].id,
            location_id=test_locations[1].id,
            note="Remote-friendly, good benefits",
            owner_id=test_user1["id"],
        ),
        models.Job(
            title="Cloud Engineer",
            description="Design and implement cloud infrastructure solutions",
            salary_min=90000,
            salary_max=130000,
            personal_rating=9,
            url="https://cloudsolutions.co.uk/careers/cloud-engineer",
            company_id=test_companies[2].id,
            location_id=test_locations[2].id,
            note="Cutting-edge technology, excellent team",
            owner_id=test_user2["id"],
        ),
        models.Job(
            title="Full Stack Developer",
            description="Work on both frontend and backend of our fintech platform",
            salary_min=85000,
            salary_max=110000,
            personal_rating=6,
            company_id=test_companies[3].id,
            location_id=test_locations[3].id,
            note="Startup environment, equity options",
            owner_id=test_user1["id"],
        ),
        models.Job(
            title="DevOps Engineer",
            description="Manage CI/CD pipelines and infrastructure automation",
            salary_min=95000,
            salary_max=140000,
            company_id=test_companies[4].id,
            location_id=test_locations[4].id,
            owner_id=test_user2["id"],
        ),
    ]

    session.add_all(jobs)
    session.commit()
    jobs = session.query(models.Job).all()

    # Add keywords to jobs
    jobs[0].keywords.extend([test_keywords[0], test_keywords[5], test_keywords[9]])  # Python, AWS, FastAPI
    jobs[1].keywords.extend([test_keywords[1], test_keywords[2]])  # JavaScript, React
    jobs[2].keywords.extend([test_keywords[5], test_keywords[6], test_keywords[7]])  # AWS, Docker, Kubernetes
    jobs[3].keywords.extend([test_keywords[0], test_keywords[1], test_keywords[3]])  # Python, JavaScript, Node.js
    jobs[4].keywords.extend([test_keywords[6], test_keywords[7], test_keywords[5]])  # Docker, Kubernetes, AWS

    jobs = session.query(models.Job).all()
    session.commit()
    return jobs


@pytest.fixture
def test_job_applications(session, test_user1, test_user2, test_jobs):
    """Create test job application data"""
    base_date = dt.datetime.now()
    job_applications = [
        models.JobApplication(
            date=base_date - dt.timedelta(days=30),
            url="https://techcorp.com/application/12345",
            job_id=test_jobs[0].id,
            status="Applied",
            note="Applied through company website",
            owner_id=test_user1["id"],
        ),
        models.JobApplication(
            date=base_date - dt.timedelta(days=25),
            url="https://linkedin.com/jobs/application/67890",
            job_id=test_jobs[1].id,
            status="Interview Scheduled",
            note="HR reached out, phone interview scheduled",
            owner_id=test_user1["id"],
        ),
        models.JobApplication(
            date=base_date - dt.timedelta(days=20),
            job_id=test_jobs[2].id,
            status="Rejected",
            note="Position filled internally",
            owner_id=test_user2["id"],
        ),
        models.JobApplication(
            date=base_date - dt.timedelta(days=15),
            url="https://startupxyz.io/apply/54321",
            job_id=test_jobs[3].id,
            status="Under Review",
            note="Submitted portfolio and references",
            owner_id=test_user1["id"],
        ),
        models.JobApplication(
            date=base_date - dt.timedelta(days=10),
            job_id=test_jobs[4].id,
            status="Offer Extended",
            note="Waiting for final decision",
            owner_id=test_user2["id"],
        ),
    ]
    session.add_all(job_applications)
    session.commit()
    for job_app in job_applications:
        session.refresh(job_app)
    return job_applications


@pytest.fixture
def test_interviews(session, test_user1, test_user2, test_job_applications, test_locations, test_persons):
    """Create test interview data"""
    base_date = dt.datetime.now()
    interviews = [
        models.Interview(
            date=base_date + dt.timedelta(days=3),
            location_id=test_locations[0].id,
            jobapplication_id=test_job_applications[1].id,  # For the "Interview Scheduled" application
            note="Technical interview with team lead",
            owner_id=test_user1["id"],
        ),
        models.Interview(
            date=base_date + dt.timedelta(days=7),
            location_id=test_locations[3].id,  # Remote location
            jobapplication_id=test_job_applications[3].id,  # For the "Under Review" application
            note="Video call with founder and CTO",
            owner_id=test_user1["id"],
        ),
        models.Interview(
            date=base_date - dt.timedelta(days=5),  # Past interview
            location_id=test_locations[2].id,
            jobapplication_id=test_job_applications[2].id,  # For the rejected application
            note="Initial screening - went well but position filled",
            owner_id=test_user2["id"],
        ),
        models.Interview(
            date=base_date + dt.timedelta(days=1),  # Tomorrow
            location_id=test_locations[4].id,  # Remote
            jobapplication_id=test_job_applications[4].id,  # For the offer extended application
            note="Final interview before decision",
            owner_id=test_user2["id"],
        ),
    ]

    session.add_all(interviews)
    session.commit()
    interviews = session.query(models.Interview).all()

    # Add interviewers to interviews using the many-to-many relationship
    interviews[0].interviewers.extend([test_persons[0], test_persons[1]])  # John Smith, Sarah Johnson
    interviews[1].interviewers.append(test_persons[3])  # Emma Davis
    interviews[2].interviewers.append(test_persons[2])  # Michael Brown
    interviews[3].interviewers.extend([test_persons[4], test_persons[2]])  # David Wilson, Michael Brown

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
                    assert value == response_value

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
        print(response.json())
        print(test_data)
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
