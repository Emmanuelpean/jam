from fastapi.testclient import TestClient
from app.main import app
from app import database, models
import sqlalchemy
import pytest
from app.oauth2 import create_access_token
from typing import List


SQLALCHEMY_DATABASE_URL = database.SQLALCHEMY_DATABASE_URL + "_test"
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def session() -> sqlalchemy.orm.Session:
    """
    Fixture that sets up and tears down a new database session for each test function.

    This fixture creates a fresh database session by creating and dropping all tables in the
    test database. It yields a session that can be used by test functions. After the test
    function completes, the session is closed.

    :yield: A new SQLAlchemy session bound to the test database.
    :rtype: sqlalchemy.orm.Session
    """
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session) -> TestClient:
    """
    Fixture that provides a test client with an overridden database dependency.

    This fixture creates a test client by overriding the default database dependency
    to use the test database session. It yields the TestClient, allowing the test
    functions to make requests to the FastAPI application.

    :param session: The database session fixture to override the database dependency.
    :yield: The FastAPI TestClient with the overridden database dependency.
    :rtype: fastapi.testclient.TestClient
    """

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(database.get_db, None)  # Clean up dependency override


def create_user(client: TestClient, **user_data) -> dict:
    """
    Helper function to create a new user via the FastAPI application.

    This function sends a POST request to the "/users/" endpoint with the provided
    user data to create a new user. It asserts that the response status code is 201
    (created), and it returns the newly created user data, including the password.

    :param client: The FastAPI TestClient to make the request.
    :param user_data: A dictionary of user attributes (e.g., email, password, username).
    :return: The created user data, including the password.
    :rtype: dict
    """
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user(client: TestClient) -> dict:
    """First test user"""
    user_data = {
        "email": "emmanuel.pean@gmail.com",
        "password": "pass123",
        "username": "emmanuelpean",
    }
    return create_user(client, **user_data)


@pytest.fixture
def test_user2(client: TestClient) -> dict:
    """Second test user"""

    user_data = {
        "email": "john@gmail.com",
        "password": "password123",
        "username": "john",
    }
    return create_user(client, **user_data)


@pytest.fixture
def token(test_user: dict) -> str:
    """
    Fixture that generates an access token for the given test user.

    This fixture uses the `create_access_token` function to generate a JWT token
    for the provided test user, which is then used for authorization in test requests.

    :param test_user: The test user for whom to generate the access token.
    :return: The generated JWT access token.
    :rtype: str
    """
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def token2(test_user2: dict) -> str:
    """
    Fixture that generates an access token for the given test user.

    This fixture uses the `create_access_token` function to generate a JWT token
    for the provided test user, which is then used for authorization in test requests.

    :param test_user: The test user for whom to generate the access token.
    :return: The generated JWT access token.
    :rtype: str
    """
    return create_access_token({"user_id": test_user2["id"]})


@pytest.fixture
def authorized_client(client: TestClient, token: str) -> TestClient:
    """
    Fixture that provides a test client with authorization headers.

    This fixture adds the generated JWT token to the headers of the FastAPI TestClient
    to simulate an authorized request, allowing the client to make requests as the
    authenticated user.

    :param client: The FastAPI TestClient to make the request.
    :param token: The JWT token to add to the Authorization header.
    :return: The FastAPI TestClient with the Authorization header set.
    :rtype: fastapi.testclient.TestClient
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def authorized_client2(client: TestClient, token2: str) -> TestClient:
    """
    Fixture that provides a test client with authorization headers.

    This fixture adds the generated JWT token to the headers of the FastAPI TestClient
    to simulate an authorized request, allowing the client to make requests as the
    authenticated user.

    :param client: The FastAPI TestClient to make the request.
    :param token: The JWT token to add to the Authorization header.
    :return: The FastAPI TestClient with the Authorization header set.
    :rtype: fastapi.testclient.TestClient
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(
    test_user: dict, session: sqlalchemy.orm.Session, test_user2: dict
) -> List[models.Post]:
    """
    Fixture that creates and returns a list of test posts.

    This fixture creates several posts in the test database for two users. It adds
    the posts to the database and commits the transaction. It then returns the list
    of all posts from the database.

    :param test_user: The first test user who owns some of the posts.
    :param session: The SQLAlchemy session to interact with the database.
    :param test_user2: The second test user who owns other posts.
    :return: A list of all posts created for the test users.
    :rtype: List[models.Post]
    """
    posts_data = [
        {"title": "1st title", "content": "1st content", "owner_id": test_user["id"]},
        {"title": "2nd title", "content": "2nd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": test_user["id"]},
        {"title": "1st title", "content": "1st content", "owner_id": test_user2["id"]},
    ]

    posts = [models.Post(**post) for post in posts_data]
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
