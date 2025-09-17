import asyncio
import os
import sys
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["DATABASE_HOSTNAME"] = "127.0.0.1"

from app.main import app
from app.database import Base, AsyncSessionLocal, async_engine
from app.models import User
from app.utils import hash as hash_password


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_setup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture()
async def test_user():
    user_data = {"email": "user1@example.com", "password": "secret"}
    async with AsyncSessionLocal() as session:
        async with session.begin():
            new_user = User(email=user_data["email"], password=hash_password(user_data["password"]))
            session.add(new_user)
        await session.refresh(new_user)
        user_dict = {"id": new_user.id, "email": new_user.email}
    return {"user": user_dict, "plain_password": user_data["password"]}


@pytest_asyncio.fixture()
async def test_user2():
    user_data = {"email": "user2@example.com", "password": "secret2"}
    async with AsyncSessionLocal() as session:
        async with session.begin():
            new_user = User(email=user_data["email"], password=hash_password(user_data["password"]))
            session.add(new_user)
        await session.refresh(new_user)
        user_dict = {"id": new_user.id, "email": new_user.email}
    return {"user": user_dict, "plain_password": user_data["password"]}


@pytest_asyncio.fixture()
async def token(async_client: httpx.AsyncClient, test_user: dict) -> str:
    form = {"username": test_user["user"]["email"], "password": test_user["plain_password"]}
    res = await async_client.post("/v2/auth/login", data=form)
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest_asyncio.fixture()
async def authorized_async_client(async_client: httpx.AsyncClient, token: str) -> httpx.AsyncClient:
    async_client.headers["Authorization"] = f"Bearer {token}"
    try:
        yield async_client
    finally:
        async_client.headers.pop("Authorization", None)


@pytest_asyncio.fixture()
async def test_posts(authorized_async_client: httpx.AsyncClient):
    posts_payload = [
        {"title": "Title 1", "content": "Content 1", "published": True},
        {"title": "Title 2", "content": "Content 2", "published": True},
        {"title": "Hidden Title", "content": "Hidden Content", "published": False},
    ]
    created = []
    for payload in posts_payload:
        res = await authorized_async_client.post("/v2/posts/", json=payload)
        assert res.status_code == 201
        created.append(res.json())
    return created
