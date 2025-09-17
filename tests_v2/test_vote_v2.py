
import pytest
from fastapi import status
from app.schemas import Vote

pytestmark = pytest.mark.asyncio

async def test_vote_create(authorized_async_client, test_posts):
    payload = Vote(post_id=test_posts[0]["id"], dir=1).model_dump()
    res = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED

async def test_vote_duplicate(authorized_async_client, test_posts):
    payload = Vote(post_id=test_posts[0]["id"], dir=1).model_dump()
    res = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    res_dup = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res_dup.status_code == status.HTTP_409_CONFLICT

async def test_vote_revoke(authorized_async_client, test_posts):
    payload = Vote(post_id=test_posts[0]["id"], dir=1).model_dump()
    res = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    revoke_payload = Vote(post_id=test_posts[0]["id"], dir=0).model_dump()
    res_revoke = await authorized_async_client.post("/v2/vote/", json=revoke_payload)
    assert res_revoke.status_code == status.HTTP_201_CREATED

async def test_vote_revoke_without_vote(authorized_async_client, test_posts):
    payload = Vote(post_id=test_posts[0]["id"], dir=0).model_dump()
    res = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND

async def test_vote_on_missing_post(authorized_async_client):
    payload = Vote(post_id=999999, dir=1).model_dump()
    res = await authorized_async_client.post("/v2/vote/", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND
