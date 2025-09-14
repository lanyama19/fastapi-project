from fastapi import status


def test_get_posts_unauthorized(client):
    res = client.get("/posts/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_posts_only_published(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    # Only 2 published posts should be returned
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert "post" in item and "votes" in item
        assert item["post"]["published"] is True
        assert isinstance(item["votes"], int)


def test_get_post_by_id_success(authorized_client, test_posts):
    target_id = test_posts[0]["id"]
    res = authorized_client.get(f"/posts/{target_id}")
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert body["post"]["id"] == target_id
    assert isinstance(body["votes"], int)


def test_get_post_not_found(authorized_client):
    res = authorized_client.get("/posts/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_create_post_success(authorized_client, test_user):
    payload = {"title": "New", "content": "Body", "published": True}
    res = authorized_client.post("/posts/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["owner_id"] == test_user["user"]["id"]


def test_update_post_owner(authorized_client):
    # Create
    create = authorized_client.post(
        "/posts/", json={"title": "t", "content": "c", "published": True}
    )
    assert create.status_code == status.HTTP_201_CREATED
    post = create.json()
    # Update
    new_data = {"title": "t2", "content": "c2", "published": False}
    res = authorized_client.put(f"/posts/{post['id']}", json=new_data)
    assert res.status_code == status.HTTP_200_OK
    updated = res.json()
    assert updated["title"] == new_data["title"]
    assert updated["content"] == new_data["content"]
    assert updated["published"] == new_data["published"]


def test_update_post_forbidden(client, authorized_client, test_user2):
    # Create by user1
    create = authorized_client.post(
        "/posts/", json={"title": "t", "content": "c", "published": True}
    )
    assert create.status_code == status.HTTP_201_CREATED
    post = create.json()

    # Login as user2 to get token
    form = {"username": test_user2["user"]["email"], "password": test_user2["plain_password"]}
    login = client.post("/login", data=form)
    assert login.status_code == status.HTTP_200_OK
    token2 = login.json()["access_token"]

    # Attempt update as user2
    res = client.put(
        f"/posts/{post['id']}",
        json={"title": "x", "content": "y", "published": True},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_delete_post_owner(authorized_client):
    create = authorized_client.post(
        "/posts/", json={"title": "t", "content": "c", "published": True}
    )
    assert create.status_code == status.HTTP_201_CREATED
    post = create.json()
    res = authorized_client.delete(f"/posts/{post['id']}")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_forbidden(client, authorized_client, test_user2):
    create = authorized_client.post(
        "/posts/", json={"title": "t", "content": "c", "published": True}
    )
    assert create.status_code == status.HTTP_201_CREATED
    post = create.json()

    form = {"username": test_user2["user"]["email"], "password": test_user2["plain_password"]}
    login = client.post("/login", data=form)
    assert login.status_code == status.HTTP_200_OK
    token2 = login.json()["access_token"]

    res = client.delete(
        f"/posts/{post['id']}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

