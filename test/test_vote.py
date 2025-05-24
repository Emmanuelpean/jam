import pytest
from app import models


@pytest.fixture
def test_vote(test_posts, session, test_user):
    """
    Fixture to create a new vote record in the database for testing.

    :param test_posts: List of test posts to be used in the vote.
    :type test_posts: list
    :param session: The SQLAlchemy session object for interacting with the database.
    :type session: Session
    :param test_user: A dictionary containing test user details.
    :type test_user: dict

    :return: The created vote object.
    :rtype: models.Vote
    """
    new_vote = models.Vote(post_id=test_posts[0].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


def test_vote_on_post(authorized_client, test_posts):
    """
    Test voting on a post.

    :param authorized_client: A pytest fixture that provides an authenticated client.
    :type authorized_client: TestClient
    :param test_posts: List of test posts to vote on.
    :type test_posts: list

    :assert response.status_code: Asserts that the status code is 201 (Created).
    :type response.status_code: int
    """
    response = authorized_client.post('/vote/', json={'post_id': test_posts[0].id, "value": 1})
    assert response.status_code == 201


def test_vote_twice_post(authorized_client, test_posts, test_vote):
    """
    Test voting twice on the same post.

    :param authorized_client: A pytest fixture that provides an authenticated client.
    :type authorized_client: TestClient
    :param test_posts: List of test posts.
    :type test_posts: list
    :param test_vote: A vote object for the test.
    :type test_vote: models.Vote

    :assert response.status_code: Asserts that the status code is 409 (Conflict).
    :type response.status_code: int
    """
    response = authorized_client.post('/vote/', json={'post_id': test_posts[0].id, "value": 1})
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote):
    """
    Test deleting a vote by setting the vote value to 0.

    :param authorized_client: A pytest fixture that provides an authenticated client.
    :type authorized_client: TestClient
    :param test_posts: List of test posts.
    :type test_posts: list
    :param test_vote: A vote object for the test.
    :type test_vote: models.Vote

    :assert response.status_code: Asserts that the status code is 201 (Created).
    :type response.status_code: int
    """
    response = authorized_client.post('/vote/', json={'post_id': test_posts[0].id, "value": 0})
    assert response.status_code == 201


def test_delete_vote_non_exist(authorized_client, test_posts):
    """
    Test deleting a vote for a non-existent vote.

    :param authorized_client: A pytest fixture that provides an authenticated client.
    :type authorized_client: TestClient
    :param test_posts: List of test posts.
    :type test_posts: list

    :assert response.status_code: Asserts that the status code is 404 (Not Found).
    :type response.status_code: int
    """
    response = authorized_client.post('/vote/', json={'post_id': test_posts[0].id, "value": 0})
    assert response.status_code == 404


def test_vote_post_non_exist(authorized_client, test_posts):
    """
    Test voting on a non-existent post.

    :param authorized_client: A pytest fixture that provides an authenticated client.
    :type authorized_client: TestClient
    :param test_posts: List of test posts.
    :type test_posts: list

    :assert response.status_code: Asserts that the status code is 404 (Not Found).
    :type response.status_code: int
    """
    response = authorized_client.post('/vote/', json={'post_id': 8000, "value": 0})
    assert response.status_code == 404


def test_vote_on_other_user_post(client, test_posts):
    """
    Test voting on a post owned by another user.

    :param client: A pytest fixture that provides a non-authorized client.
    :type client: TestClient
    :param test_posts: List of test posts.
    :type test_posts: list

    :assert response.status_code: Asserts that the status code is 401 (Unauthorized).
    :type response.status_code: int
    """
    response = client.post('/vote/', json={'post_id': test_posts[3].id, "value": 1})
    assert response.status_code == 401
