
import pytest
from fastapi import status
from app.schemas import UserCreate, UserOut

pytestmark = pytest.mark.asyncio

async def test_create_user(async_client):
    payload = UserCreate(email="newuser@example.com", password="secret").model_dump()
    res = await async_client.post("/v2/users/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = UserOut.model_validate(res.json())
    assert data.email == payload["email"]

async def test_get_user(async_client, test_user):
    user_id = test_user["user"]["id"]
    res = await async_client.get(f"/v2/users/{user_id}")
    assert res.status_code == status.HTTP_200_OK
    data = UserOut.model_validate(res.json())
    assert data.id == user_id

async def test_get_user_not_found(async_client):
    res = await async_client.get("/v2/users/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND
