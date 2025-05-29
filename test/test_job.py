import pytest

from app import schemas, models


# ---------------------------------------------------- GETTING POSTS ---------------------------------------------------


def test_get_all_jobs(authorized_client1, test_user1: dict, test_jobs):
    response = authorized_client1.get("/jobs")
    jobs = [schemas.JobOut(**job) for job in response.json()]
    assert (len(jobs)) == len([job for job in test_jobs if job.owner_id == test_user1["id"]])
    assert response.status_code == 200


def test_unauthorised_user_get_all_posts(client, test_jobs):
    response = client.get("/jobs/")
    assert response.status_code == 401


def test_unauthorised_user_get_one_post(client, test_jobs):
    response = client.get(f"/jobs/{test_jobs[0].id}")
    assert response.status_code == 401


def test_wrong_user_get_one_post(authorized_client2, test_jobs):
    response = authorized_client2.get(f"/jobs/{test_jobs[0].id}")
    assert response.status_code == 401


def test_get_one_post_not_exist(authorized_client1, test_jobs):
    response = authorized_client1.get(f"/jobs/100")
    assert response.status_code == 404


def test_get_one_post(authorized_client1, test_jobs):
    response = authorized_client1.get(f"jobs/{test_jobs[0].id}")
    job = schemas.PostOut(**response.json())
    assert job.Post.id == test_jobs[0].id
    assert job.Post.content == test_jobs[0].content
    assert job.Post.title == test_jobs[0].title


# --------------------------------------------------- CREATING POSTS ---------------------------------------------------


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("new 1st title", "new 1st content", True),
        ("new 2nd title", "new 2nd content", True),
        ("new 4th title", "new 4th content", False),
    ],
)
def test_create_post(title, content, published, authorized_client1, test_user1: dict):
    post_data = {"title": title, "content": content, "published": published}
    response = authorized_client1.job("/jobs", json=post_data)
    created_post = schemas.Post(**response.json())
    assert response.status_code == 201
    for attr in post_data:
        assert getattr(created_post, attr) == post_data[attr]
    assert created_post.owner_id == test_user1["id"]


def test_create_post_default_published_true(authorized_client1, test_user1: dict):
    post_data = {"title": "some title", "content": "some content"}
    response = authorized_client1.job("/jobs", json=post_data)
    created_post = schemas.Post(**response.json())
    assert response.status_code == 201
    for attr in post_data:
        assert getattr(created_post, attr) == post_data[attr]
    assert created_post.published == True
    assert created_post.owner_id == test_user1["id"]


def test_unauthorised_user_create_post(client):
    post_data = {"title": "some title", "content": "some content"}
    response = client.job("/jobs", json=post_data)
    assert response.status_code == 401


# --------------------------------------------------- DELETING POSTS ---------------------------------------------------


def test_unauthorised_user_create_post(client, test_jobs):
    response = client.delete(f"/jobs/{test_jobs[0].id}")
    assert response.status_code == 401


def delete_post_success(authorized_client, test_posts: list[models.Post]):
    response = authorized_client.delete(f"/jobs/{test_posts[0].id}")
    assert response.status_code == 204


def delete_post_non_exist(authorized_client):
    response = authorized_client.delete(f"/jobs/1000")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client1, test_jobs):
    response = authorized_client1.delete(f"/jobs/{test_jobs[3].id}")
    assert response.status_code == 403


# --------------------------------------------------- UPDATING POSTS ---------------------------------------------------


def test_update_post(authorized_client1, test_user1, test_jobs):
    post_data = {
        "title": "some title",
        "content": "some content",
        "id": test_jobs[0].id,
    }
    response = authorized_client1.put(f"/jobs/{post_data['id']}", json=post_data)
    updated_post = schemas.Post(**response.json(), owner=test_user1)
    assert response.status_code == 200
    for attr in post_data:
        assert getattr(updated_post, attr) == post_data[attr]


def test_update_other_user_post(authorized_client1, test_jobs):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_jobs[3].id,
    }
    res = authorized_client1.put(f"/jobs/{test_jobs[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_jobs):
    res = client.put(f"/jobs/{test_jobs[0].id}")
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client1, test_jobs):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_jobs[3].id,
    }
    res = authorized_client1.put(f"/jobs/8000000", json=data)

    assert res.status_code == 404
