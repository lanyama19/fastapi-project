from fastapi import status
from app.schemas import Token


def test_root_ok(client):
    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert isinstance(body.get("message"), str)


def test_login_success(client, test_user):
    form = {
        "username": test_user["user"]["email"],
        "password": test_user["plain_password"],
    }
    res = client.post("/v1/auth/login", data=form)
    assert res.status_code == status.HTTP_200_OK
    token = Token.model_validate(res.json())
    assert isinstance(token.access_token, str) and token.access_token
    assert token.token_type == "bearer"


def test_login_wrong_password(client, test_user):
    form = {"username": test_user["user"]["email"], "password": "wrong"}
    res = client.post("/v1/auth/login", data=form)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_login_nonexistent_user(client):
    form = {"username": "nouser@example.com", "password": "secret"}
    res = client.post("/v1/auth/login", data=form)
    assert res.status_code == status.HTTP_403_FORBIDDEN
