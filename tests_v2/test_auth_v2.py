
import pytest
from fastapi import status
from app.schemas import Token

pytestmark = pytest.mark.asyncio

async def test_login_success(async_client, test_user):
    form = {
        "username": test_user["user"]["email"],
        "password": test_user["plain_password"],
    }
    res = await async_client.post("/v2/auth/login", data=form)
    assert res.status_code == status.HTTP_200_OK
    token = Token.model_validate(res.json())
    assert isinstance(token.access_token, str) and token.access_token
    assert token.token_type == "bearer"

async def test_login_wrong_password(async_client, test_user):
    form = {"username": test_user["user"]["email"], "password": "wrong"}
    res = await async_client.post("/v2/auth/login", data=form)
    assert res.status_code == status.HTTP_403_FORBIDDEN

async def test_login_nonexistent_user(async_client):
    form = {"username": "nouser@example.com", "password": "secret"}
    res = await async_client.post("/v2/auth/login", data=form)
    assert res.status_code == status.HTTP_403_FORBIDDEN
