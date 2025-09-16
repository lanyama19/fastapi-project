from typing import Generator
from pathlib import Path
import sys
import os

# Ensure project root is on sys.path so `import app` works
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Force DB host to local when running tests outside Docker
os.environ["DATABASE_HOSTNAME"] = "127.0.0.1"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal, get_db


@pytest.fixture()
def session() -> Generator:
    # WARNING: This drops and recreates all tables in the configured database.
    # Ensure your env points to a dedicated TEST database before running.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield session
        finally:
            pass

    # Override the app dependency to use the PostgreSQL-backed test session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def test_user(client):
    payload = {"email": "user1@example.com", "password": "secret"}
    res = client.post("/v1/users/", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    return {"user": data, "plain_password": payload["password"]}


@pytest.fixture()
def test_user2(client):
    payload = {"email": "user2@example.com", "password": "secret2"}
    res = client.post("/v1/users/", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    return {"user": data, "plain_password": payload["password"]}


@pytest.fixture()
def token(client, test_user):
    # Obtain JWT via login endpoint
    form = {
        "username": test_user["user"]["email"],
        "password": test_user["plain_password"],
    }
    res = client.post("/v1/auth/login", data=form)
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture()
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture()
def test_posts(authorized_client, test_user, test_user2):
    posts_payload = [
        {"title": "Title 1", "content": "Content 1", "published": True},
        {"title": "Title 2", "content": "Content 2", "published": True},
        {"title": "Hidden Title", "content": "Hidden Content", "published": False},
    ]
    created = []
    for p in posts_payload:
        res = authorized_client.post("/v1/posts/", json=p)
        assert res.status_code == 201, res.text
        created.append(res.json())
    return created