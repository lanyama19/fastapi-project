import pytest
from fastapi import status
from app.schemas import PostCreate, Post, PostWithVotes

pytestmark = pytest.mark.asyncio

async def test_get_posts_unauthorized(async_client):
    res = await async_client.get("/v2/posts/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

async def test_get_posts_only_published(authorized_async_client, test_posts):
    res = await authorized_async_client.get("/v2/posts/")
    assert res.status_code == status.HTTP_200_OK
    data = [PostWithVotes.model_validate(item) for item in res.json()]
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert item.post.published is True
        assert isinstance(item.votes, int)

async def test_get_post_by_id_success(authorized_async_client, test_posts):
    target_id = test_posts[0]["id"]
    res = await authorized_async_client.get(f"/v2/posts/{target_id}")
    assert res.status_code == status.HTTP_200_OK
    body = PostWithVotes.model_validate(res.json())
    assert body.post.id == target_id
    assert isinstance(body.votes, int)

async def test_get_post_not_found(authorized_async_client):
    res = await authorized_async_client.get("/v2/posts/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND

async def test_create_post_success(authorized_async_client, test_user):
    payload = PostCreate(title="New v2", content="Body v2", published=True)
    res = await authorized_async_client.post("/v2/posts/", json=payload.model_dump())
    assert res.status_code == status.HTTP_201_CREATED
    data = Post.model_validate(res.json())
    assert data.title == payload.title
    assert data.content == payload.content
    assert data.owner_id == test_user["user"]["id"]
    assert data.owner.id == test_user["user"]["id"]

async def test_update_post_owner(authorized_async_client, test_posts):
    post_to_update = test_posts[0]
    new_data = PostCreate(title="t2_v2", content="c2_v2", published=False)
    res = await authorized_async_client.put(f"/v2/posts/{post_to_update['id']}", json=new_data.model_dump())
    assert res.status_code == status.HTTP_200_OK
    updated = Post.model_validate(res.json())
    assert updated.title == new_data.title
    assert updated.content == new_data.content
    assert updated.published == new_data.published

async def test_update_post_forbidden(async_client, test_user2, test_posts):
    post_to_update = test_posts[0]
    # Login as user2 to get token
    form = {"username": test_user2["user"]["email"], "password": test_user2["plain_password"]}
    login_res = await async_client.post("/v2/auth/login", data=form)
    assert login_res.status_code == 200
    token2 = login_res.json()["access_token"]

    # Attempt update as user2
    new_data = PostCreate(title="x_v2", content="y_v2", published=True)
    res = await async_client.put(
        f"/v2/posts/{post_to_update['id']}",
        json=new_data.model_dump(),
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

async def test_delete_post_owner(authorized_async_client, test_posts):
    post_to_delete = test_posts[0]
    res = await authorized_async_client.delete(f"/v2/posts/{post_to_delete['id']}")
    assert res.status_code == status.HTTP_204_NO_CONTENT

async def test_delete_post_forbidden(async_client, test_user2, test_posts):
    post_to_delete = test_posts[0]
    # Login as user2 to get token
    form = {"username": test_user2["user"]["email"], "password": test_user2["plain_password"]}
    login_res = await async_client.post("/v2/auth/login", data=form)
    assert login_res.status_code == 200
    token2 = login_res.json()["access_token"]

    # Attempt delete as user2
    res = await async_client.delete(
        f"/v2/posts/{post_to_delete['id']}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN