from typing import List
import pytest
from app import schemas, models


# ---------------------------------------------------- GETTING POSTS ---------------------------------------------------


def test_get_all_posts(
    authorized_client, test_user: dict, test_posts: List[models.Post]
):
    response = authorized_client.get("/posts")
    posts = [schemas.PostOut(**post) for post in response.json()]
    assert (len(posts)) == len(
        [post for post in test_posts if post.owner_id == test_user["id"]]
    )
    assert response.status_code == 200


def test_unauthorised_user_get_all_posts(client, test_posts: List[models.Post]):
    response = client.get("/posts/")
    assert response.status_code == 401


def test_unauthorised_user_get_one_post(client, test_posts: List[models.Post]):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_wrong_user_get_one_post(authorized_client2, test_posts):
    response = authorized_client2.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_get_one_post_not_exist(authorized_client, test_posts: List[models.Post]):
    response = authorized_client.get(f"/posts/100")
    assert response.status_code == 404


def test_get_one_post(authorized_client, test_posts: List[models.Post]):
    response = authorized_client.get(f"posts/{test_posts[0].id}")
    post = schemas.PostOut(**response.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


# --------------------------------------------------- CREATING POSTS ---------------------------------------------------


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("new 1st title", "new 1st content", True),
        ("new 2nd title", "new 2nd content", True),
        ("new 4th title", "new 4th content", False),
    ],
)
def test_create_post(title, content, published, authorized_client, test_user: dict):
    post_data = {"title": title, "content": content, "published": published}
    response = authorized_client.post("/posts", json=post_data)
    created_post = schemas.Post(**response.json())
    assert response.status_code == 201
    for attr in post_data:
        assert getattr(created_post, attr) == post_data[attr]
    assert created_post.owner_id == test_user["id"]


def test_create_post_default_published_true(authorized_client, test_user: dict):
    post_data = {"title": "some title", "content": "some content"}
    response = authorized_client.post("/posts", json=post_data)
    created_post = schemas.Post(**response.json())
    assert response.status_code == 201
    for attr in post_data:
        assert getattr(created_post, attr) == post_data[attr]
    assert created_post.published == True
    assert created_post.owner_id == test_user["id"]


def test_unauthorised_user_create_post(client):
    post_data = {"title": "some title", "content": "some content"}
    response = client.post("/posts", json=post_data)
    assert response.status_code == 401


# --------------------------------------------------- DELETING POSTS ---------------------------------------------------


def test_unauthorised_user_create_post(client, test_posts: List[models.Post]):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def delete_post_success(authorized_client, test_posts: List[models.Post]):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204


def delete_post_non_exist(authorized_client):
    response = authorized_client.delete(f"/posts/1000")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, test_posts: List[models.Post]):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403


# --------------------------------------------------- UPDATING POSTS ---------------------------------------------------


def test_update_post(authorized_client, test_user, test_posts: List[models.Post]):
    post_data = {
        "title": "some title",
        "content": "some content",
        "id": test_posts[0].id,
    }
    response = authorized_client.put(f"/posts/{post_data['id']}", json=post_data)
    updated_post = schemas.Post(**response.json(), owner=test_user)
    assert response.status_code == 200
    for attr in post_data:
        assert getattr(updated_post, attr) == post_data[attr]


def test_update_other_user_post(authorized_client, test_posts: List[models.Post]):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_posts[3].id,
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_posts: List[models.Post]):
    res = client.put(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client, test_posts: List[models.Post]):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_posts[3].id,
    }
    res = authorized_client.put(f"/posts/8000000", json=data)

    assert res.status_code == 404
