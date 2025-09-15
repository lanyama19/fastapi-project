from fastapi import status
from app.schemas import PostCreate, Post, Vote


def _create_post(authorized_client):
    payload = PostCreate(title="vote", content="body", published=True)
    res = authorized_client.post("/posts/", json=payload.model_dump())
    assert res.status_code == status.HTTP_201_CREATED
    return Post.model_validate(res.json()).id


def test_vote_requires_auth(client):
    # get_current_user should raise 401 before checking post existence
    res = client.post("/vote/", json=Vote(post_id=1, dir=1).model_dump())
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_vote_add_success(authorized_client):
    post_id = _create_post(authorized_client)
    res = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=1).model_dump())
    assert res.status_code == status.HTTP_201_CREATED


def test_vote_duplicate_conflict(authorized_client):
    post_id = _create_post(authorized_client)
    r1 = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=1).model_dump())
    assert r1.status_code == status.HTTP_201_CREATED
    r2 = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=1).model_dump())
    assert r2.status_code == status.HTTP_409_CONFLICT


def test_unvote_success(authorized_client):
    post_id = _create_post(authorized_client)
    r1 = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=1).model_dump())
    assert r1.status_code == status.HTTP_201_CREATED
    r2 = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=0).model_dump())
    assert r2.status_code == status.HTTP_201_CREATED


def test_unvote_missing_returns_404(authorized_client):
    post_id = _create_post(authorized_client)
    # directly try to un-vote without prior vote
    res = authorized_client.post("/vote/", json=Vote(post_id=post_id, dir=0).model_dump())
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_vote_nonexistent_post(authorized_client):
    res = authorized_client.post("/vote/", json=Vote(post_id=999999, dir=1).model_dump())
    assert res.status_code == status.HTTP_404_NOT_FOUND
