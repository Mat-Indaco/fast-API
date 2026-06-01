from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_login():

    client.post(
        "/users/",
        json={
            "username": "admin",
            "email": "admin@test.com",
            "full_name": "Admin",
            "password": "1234",
        },
    )
    response = client.post("/login", data={"username": "admin", "password": "1234"})
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_usuario_inexistente():
    """Login con usuario que no existe devuelve 401."""
    response = client.post(
        "/login",
        data={"username": "noexisto", "password": "algo"},
    )

    assert response.status_code == 401


def test_endpoint_protegido_sin_token():
    """Acceder a un endpoint protegido sin token devuelve 401."""
    response = client.get("/users/")
    assert response.status_code == 401


def test_endpoint_protegido_con_token_invalido():
    """Acceder con un token inventado devuelve 401."""
    response = client.get(
        "/users/",
        headers={"Authorization": "Bearer tokenfalso123"},
    )
    assert response.status_code == 401
