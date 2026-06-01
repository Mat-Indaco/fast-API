

def test_create_item(client):

    client.post(
        "/users/",
        json={
            "username": "itemuser",
            "email": "item@test.com",
            "full_name": "Item User",
            "password": "1234",
        },
    )

    login = client.post(
        "/login",
        data={
            "username": "itemuser",
            "password": "1234"
        },
    )

    token = login.json()["access_token"]

    response = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Notebook",
            "description": "Gaming",
            "cant": 1
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Notebook"

def test_item_repetido_suma_cantidad(client):

    client.post(
        "/users/",
        json={
            "username": "sumuser",
            "email": "sum@test.com",
            "full_name": "Sum User",
            "password": "1234",
        },
    )

    login = client.post(
        "/login",
        data={
            "username": "sumuser",
            "password": "1234"
        },
    )

    token = login.json()["access_token"]

    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Mouse",
            "description": "Gamer",
            "cant": 2
        }
    )

    response = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Mouse",
            "description": "Gamer",
            "cant": 3
        }
    )

    data = response.json()

    assert data["cant"] == 5