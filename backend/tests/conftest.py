"""
This module is designed to facilitate testing and database interaction in the application. It includes utility functions,
fixtures, and configurations for setting up and managing the SQLAlchemy database, test users, test tokens, and mock
clients for API testing. The provided components streamline testing by enabling convenient access to preconfigured
resources.

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
import os

from app import models, database, schemas
from app.eis import models as eis_models
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
    create_interviews,
    create_job_alert_emails,
    create_scraped_jobs,
    create_service_logs,
    create_job_application_updates,
    create_settings,
)
from tests.utils.seed_database import reset_database

SQLALCHEMY_DATABASE_URL = database.SQLALCHEMY_DATABASE_URL + "_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def find_non_owned(entries: list, owner_id: int) -> int:
    """Find an entry not owned by the specified owner_id.
    :param entries: List of entries to search.
    :param owner_id: The owner ID to exclude."""

    for entry in entries:
        if entry.owner_id != owner_id:
            return entry.id
    raise AssertionError("No non-owned entry found")


@pytest.fixture
def session() -> Generator[orm.Session, Any, None]:
    """Fixture that sets up and tears down a new database session for each test function.
    This fixture creates a fresh database session by creating and dropping all tables in the
    test database. It yields a session that can be used by test functions. After the test
    function completes, the session is closed.
    :yield: A new SQLAlchemy session bound to the test database."""

    reset_database(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
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
def test_users(session) -> list[models.User]:
    """Create test user data"""

    return create_users(session)


@pytest.fixture
def tokens(test_users) -> list[str]:
    """Fixture that generates access tokens for the given test users."""

    return [create_access_token({"user_id": user.id}) for user in test_users]


@pytest.fixture
def authorised_clients(client: TestClient, tokens: list[str]) -> list[TestClient]:
    """Fixture that provides a list of authenticated test clients."""

    clients = []
    for token in tokens:
        authorized_client = TestClient(client.app)
        authorized_client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
        clients.append(authorized_client)
    return clients


@pytest.fixture
def admin_client(authorised_clients) -> TestClient:
    """Fixture for an admin client."""
    return authorised_clients[1]


@pytest.fixture
def admin_user(test_users) -> models.User:
    """Fixture for an admin user."""
    user = test_users[1]
    assert user.is_admin
    return user


@pytest.fixture
def test_client(authorised_clients) -> TestClient:
    """Fixture for a non-admin client."""
    return authorised_clients[0]


@pytest.fixture
def test_user(test_users) -> models.User:
    """Fixture for a non-admin user."""
    user = test_users[0]
    assert not user.is_admin
    return user


@pytest.fixture
def test_other_client(authorised_clients) -> TestClient:
    """Fixture for a non-admin client."""
    return authorised_clients[2]


@pytest.fixture
def test_other_user(test_users) -> models.User:
    """Fixture for a non-admin user."""
    user = test_users[2]
    assert not user.is_admin
    return user


@pytest.fixture
def test_keywords(session, test_users) -> list[models.Keyword]:
    """Create test keyword data"""

    return create_keywords(session, test_users)


@pytest.fixture
def test_aggregators(session, test_users) -> list[models.Aggregator]:
    """Create test aggregator data"""

    return create_aggregators(session, test_users)


@pytest.fixture
def test_locations(session, test_users) -> list[models.Location]:
    """Create test location data"""

    return create_locations(session, test_users)


@pytest.fixture
def test_companies(session, test_users) -> list[models.Company]:
    """Create test company data"""

    return create_companies(session, test_users)


@pytest.fixture
def test_persons(session, test_users, test_companies) -> list[models.Person]:
    """Create test person data"""

    return create_people(session, test_users, test_companies)


@pytest.fixture
def persons_unauthorised_data(test_companies) -> tuple[list[dict], int]:
    """Create test person data with incorrect company_id for access control testing"""

    owner_id = 1
    company_id = find_non_owned(test_companies, owner_id)
    return [{"first_name": "A", "last_name": "B", "company_id": company_id, "owner_id": owner_id}], owner_id


@pytest.fixture
def test_persons_unauthorised(
    session, test_users, test_companies, persons_unauthorised_data
) -> tuple[list[models.Person], int]:
    """Create test person data with incorrect company_id for access control testing"""

    data, owner_id = persons_unauthorised_data
    return create_people(session, test_users, test_companies, data), owner_id


@pytest.fixture
def test_files(session, test_users) -> list[models.File]:
    """Create test files for job applications"""

    return create_files(session, test_users)


@pytest.fixture
def test_jobs(
    session, test_users, test_companies, test_locations, test_keywords, test_persons, test_aggregators, test_files
) -> list[models.Job]:
    """Create test job data"""

    return create_jobs(
        session, test_keywords, test_persons, test_users, test_companies, test_locations, test_aggregators, test_files
    )


@pytest.fixture
def jobs_unauthorised_data(
    session,
    test_users,
    test_companies,
    test_locations,
    test_keywords,
    test_persons,
    test_aggregators,
    test_files,
) -> tuple[list[dict], int, list[dict], list[dict]]:
    """Create test person data with incorrect company_id, location_id, keyword ids and person ids for access control testing"""

    owner_id = 1
    company_id = find_non_owned(test_companies, owner_id)
    location_id = find_non_owned(test_locations, owner_id)
    job_keyword_mapping = [{"job_id": 1, "keyword_ids": [find_non_owned(test_keywords, owner_id)]}]
    job_contact_mapping = [{"job_id": 1, "person_ids": [find_non_owned(test_persons, owner_id)]}]
    data = [
        {
            "title": "A",
            "company_id": company_id,
            "location_id": location_id,
            "owner_id": owner_id,
        }
    ]
    return data, owner_id, job_keyword_mapping, job_contact_mapping


@pytest.fixture
def test_jobs_unauthorised(
    session,
    test_users,
    test_companies,
    test_locations,
    test_keywords,
    test_persons,
    test_aggregators,
    test_files,
    jobs_unauthorised_data,
) -> tuple[list[models.Job], int]:
    """Create test person data with incorrect company_id, location_id, keyword ids and person ids for access control testing"""

    data, owner_id, job_keyword_mapping, job_contact_mapping = jobs_unauthorised_data
    jobs = create_jobs(
        session,
        test_keywords,
        test_persons,
        test_users,
        test_companies,
        test_locations,
        test_aggregators,
        test_files,
        data,
        job_keyword_mapping,
        job_contact_mapping,
    )
    return jobs, owner_id


@pytest.fixture
def test_interviews(session, test_users, test_jobs, test_locations, test_persons) -> list[models.Interview]:
    """Create test interview data"""

    return create_interviews(session, test_persons, test_users, test_locations, test_jobs)


@pytest.fixture
def interviews_unauthorised_data(
    session, test_users, test_jobs, test_locations, test_persons
) -> tuple[list[dict], int, list[dict]]:
    """Create test interview data with incorrect job_id for access control testing"""

    owner_id = 1
    job_id = find_non_owned(test_jobs, owner_id)
    data = [{"job_id": job_id, "date": str(dt.datetime.now()), "owner_id": owner_id, "type": "phone"}]
    interview_interviewer_mappings = [{"interview_id": 1, "person_ids": [find_non_owned(test_persons, owner_id)]}]
    return data, owner_id, interview_interviewer_mappings


@pytest.fixture
def test_interviews_unauthorised(
    session, test_users, test_jobs, test_locations, test_persons, interviews_unauthorised_data
) -> tuple[list[models.Interview], int]:
    """Create test interview data with incorrect job_id for access control testing"""

    data, owner_id, interview_interviewer_mappings = interviews_unauthorised_data
    interviews = create_interviews(
        session,
        test_persons,
        test_users,
        test_locations,
        test_jobs,
        data,
        interview_interviewer_mappings,
    )
    return interviews, owner_id


@pytest.fixture
def test_job_application_updates(session, test_users, test_jobs) -> list[models.JobApplicationUpdate]:
    """Create test job application update data"""

    return create_job_application_updates(session, test_users, test_jobs)


@pytest.fixture
def job_application_updates_unauthorised_data(session, test_users, test_jobs) -> tuple[list[dict], int]:
    """Create test job application update data with incorrect job_id for access control testing"""

    owner_id = 1
    job_id = find_non_owned(test_jobs, owner_id)
    data = [
        {
            "job_id": job_id,
            "date": str(dt.datetime.now()),
            "type": "received",
            "owner_id": owner_id,
            "note": "Test note",
        }
    ]
    return data, owner_id


@pytest.fixture
def test_job_application_updates_unauthorised(
    session, test_users, test_jobs, job_application_updates_unauthorised_data
) -> tuple[list[models.JobApplicationUpdate], int]:
    """Create test job application update data with incorrect job_id for access control testing"""

    data, owner_id = job_application_updates_unauthorised_data
    updates = create_job_application_updates(session, test_users, test_jobs, data)
    return updates, owner_id


# ---------------------------------------------------- EIS Fixtures ----------------------------------------------------


@pytest.fixture
def test_job_alert_emails(session, test_users, test_service_logs) -> list[eis_models.JobAlertEmail]:
    """Create test job alert emails"""

    return create_job_alert_emails(session, test_users, test_service_logs)


@pytest.fixture
def test_scraped_jobs(session, test_users, test_job_alert_emails) -> list[eis_models.ScrapedJob]:
    """Create test job alert email jobs"""

    return create_scraped_jobs(session, test_job_alert_emails, test_users)


@pytest.fixture
def test_service_logs(session) -> list[eis_models.EisServiceLog]:
    """Create test service logs"""

    return create_service_logs(session)


@pytest.fixture
def test_settings(session) -> list[models.Setting]:
    """Create test settings data"""

    return create_settings(session)


def open_file(filepath: str) -> str:
    """Helper function to open a text file from the resources directory.
    :param filepath: The name of the file located in the resources directory"""

    base_dir = os.path.dirname(__file__)  # directory of this test file
    filepath = os.path.join(base_dir, "resources", filepath)
    with open(filepath, "r") as ofile:
        return ofile.read()


def assert_ownership(item: list | dict, owner_id: int) -> None:
    """Assert that all items in a list belong to the specified owner.
    :param item: The item or list of items to check.
    :param owner_id: The expected owner ID."""

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
    - test_data: str - name of pytest fixture providing list of test objects
    - update_data: dict - example data for updating an existing object
    - create_data: list[dict] - example data for creating new objects
    - required_fixture: str or list[str] - name(s) of pytest fixture(s) for the post operations
    - get_unauthorised_fixture: str - name of pytest fixture providing data for access tests with incorrect ownership
    - unauthorised_data_fixture: str - name of pytest fixture providing data for creation tests  with incorrect ownership
    - admin_only: bool - if True, only admin users can access the endpoint
    """

    endpoint: str = ""
    admin_only: bool = False
    create_schema = None
    out_schema = None
    test_data: str = ""
    update_data: dict = None
    create_data: list[dict] = None
    required_fixture: str = None
    get_unauthorised_fixture: str = None
    unauthorised_data_fixture = None

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

        # Use the test data keys for comparison
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

        if isinstance(self.required_fixture, list):
            for fixture in self.required_fixture:
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

    def test_get_all_data_only_authorised(
        self,
        authorised_clients,
        request,
    ) -> None:

        if self.get_unauthorised_fixture:
            owner_id = request.getfixturevalue(self.get_unauthorised_fixture)[1]
            response = self.get_all(authorised_clients[owner_id - 1])
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            print(data)
            if data:
                assert_ownership(data, owner_id)

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

    def test_post_unauthorised(
        self,
        client,
    ) -> None:
        response = self.post(client, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_data_only_authorised(
        self,
        authorised_clients,
        request,
    ) -> None:

        if self.unauthorised_data_fixture:
            data, owner_id = request.getfixturevalue(self.unauthorised_data_fixture)[:2]
            for datum in data:
                datum = {key: value for key, value in datum.items() if key not in ("id", "owner_id")}
                response = self.post(authorised_clients[owner_id - 1], datum)
                assert response.status_code == status.HTTP_201_CREATED
                assert_ownership(data, owner_id)

    # ------------------------------------------------------- PUT ------------------------------------------------------

    def test_put_success(
        self,
        authorised_clients,
        request,
    ) -> None:
        request.getfixturevalue(self.test_data)
        # noinspection PyTypeChecker
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


class AdminCRUDTestBase:
    """Base class for CRUD tests on FastAPI routes.

    Subclasses must override:
    - endpoint: str - base URL path for the resource (e.g. "/aggregators")
    - create_schema: Pydantic model class for creation validation (e.g. schemas.AggregatorCreate)
    - out_schema: Pydantic model class for output validation (e.g. schemas.AggregatorOut)
    - test_data: str - name of pytest fixture providing list of test objects
    - update_data: dict - example data for updating an existing object
    - create_data: list[dict] - example data for creating new objects
    - required_fixture: str or list[str] - name(s) of pytest fixture(s) for the post operations
    - get_unauthorised_fixture: str - name of pytest fixture providing data for access tests with incorrect ownership
    - unauthorised_data_fixture: str - name of pytest fixture providing data for creation tests  with incorrect ownership
    - admin_only: bool - if True, only admin users can access the endpoint
    """

    endpoint: str = ""
    create_schema = None
    out_schema = None
    test_data: str = ""
    update_data: dict = None
    create_data: list[dict] = None
    required_fixture: str = None
    get_unauthorised_fixture: str = None
    unauthorised_data_fixture = None

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

        # Use the test data keys for comparison
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

        if isinstance(self.required_fixture, list):
            for fixture in self.required_fixture:
                request.getfixturevalue(fixture)

    # ------------------------------------------------------- GET ------------------------------------------------------

    def test_get_all_success(
        self,
        admin_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_all(admin_client)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(test_data, response.json())

    def test_get_all_unauthorized(
        self,
        client,
    ) -> None:
        response = self.get_all(client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_one_success(
        self,
        admin_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(admin_client, test_data[0].id)
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

    def test_get_one_non_admin(
        self,
        test_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.get_one(test_client, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_one_non_exist(
        self,
        admin_client,
    ) -> None:
        response = self.get_one(admin_client, 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_post_success(
        self,
        admin_client,
    ) -> None:

        for create_data in self.create_data:
            create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
            response = self.post(admin_client, create_data)
            assert response.status_code == status.HTTP_201_CREATED
            self.check_output(create_data, response.json())

    def test_post_unauthorised(
        self,
        client,
    ) -> None:
        response = self.post(client, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_non_admin(
        self,
        test_client,
    ) -> None:

        for create_data in self.create_data:
            create_data = {key: value for key, value in create_data.items() if key not in ("id", "owner_id")}
            response = self.post(test_client, create_data)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    # ------------------------------------------------------- PUT ------------------------------------------------------

    def test_put_success(
        self,
        admin_client,
        request,
    ) -> None:
        request.getfixturevalue(self.test_data)
        # noinspection PyTypeChecker
        response = self.put(admin_client, self.update_data["id"], self.update_data)
        assert response.status_code == status.HTTP_200_OK
        self.check_output(self.update_data, response.json())

    def test_put_empty_body(
        self,
        admin_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(admin_client, test_data[0].id, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_put_non_exist(
        self,
        admin_client,
    ) -> None:
        response = self.put(admin_client, 999999, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_unauthorized(
        self,
        client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_non_admin(
        self,
        test_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.put(test_client, test_data[0].id, {"name": "Test"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    def test_delete_success(
        self,
        admin_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(admin_client, test_data[0].id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_exist(
        self,
        admin_client,
    ) -> None:
        response = self.delete(admin_client, 999999)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthorised(
        self,
        client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(client, test_data[0].id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_non_admin(
        self,
        test_client,
        request,
    ) -> None:
        test_data = request.getfixturevalue(self.test_data)
        response = self.delete(test_client, test_data[0].id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
