
def test_create_user(client):

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


def test_get_users(client):
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
def test_create_user_username_duplicado(client):

    client.post(
        "/users/",
        json={
            "username": "matias",
            "email": "matias@test.com",
            "full_name": "Matias",
            "password": "1234",
        },
    )

    response = client.post(
        "/users/",
        json={
            "username": "matias",
            "email": "otro@test.com",
            "full_name": "Otro",
            "password": "1234",
        },
    )

    assert response.status_code == 409

def test_create_user_email_duplicado(client):

    client.post(
        "/users/",
        json={
            "username": "user1",
            "email": "same@test.com",
            "full_name": "User1",
            "password": "1234",
        },
    )

    response = client.post(
        "/users/",
        json={
            "username": "user2",
            "email": "same@test.com",
            "full_name": "User2",
            "password": "1234",
        },
    )

    assert response.status_code == 409

def test_admin_no_puede_borrarse(client):

    client.post(
        "/users/",
        json={
            "username": "admin_delete",
            "email": "admin@test.com",
            "full_name": "Admin",
            "password": "1234",
            "role": "admin",
        },
    )

    login = client.post(
        "/login",
        data={
            "username": "admin_delete",
            "password": "1234"
        },
    )

    token = login.json()["access_token"]

    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400