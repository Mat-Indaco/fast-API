from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_create_user():

    response = client.post(
        "/users/",
        json={
            "username": "matias",
            "email": "matias@test.com",
            "full_name": "Matias Indaco",
            "password": "1234",
            "role": "user",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "matias"
    assert data["email"] == "matias@test.com"


def test_get_users():
    client.post(
        "/users/",
        json={
            "username": "admin",
            "email": "admin@test.com",
            "full_name": "Admin",
            "password": "1234",
            "role": "user",
        },
    )

    login_response = client.post(
        "/login", data={"username": "admin", "password": "1234"}
    )

    token = login_response.json()["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
