from fastapi import status
from app.schemas import UserOut


def test_get_user_success(client, test_user):
    user_id = test_user["user"]["id"]
    res = client.get(f"/users/{user_id}")
    assert res.status_code == status.HTTP_200_OK
    data = UserOut.model_validate(res.json())
    assert data.id == user_id
    assert data.email == test_user["user"]["email"]


def test_get_user_not_found(client):
    res = client.get("/users/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND
