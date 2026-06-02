

def crear_usuario_y_login(client, username, email, role="user", password="1234"):
    client.post(
        "/users/",
        json={
            "username": username,
            "email": email,
            "full_name": username,
            "password": password,
            "role": role,
        },
    )
    login = client.post("/login", data={"username": username, "password": password})
    return login.json()["access_token"]
 

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
        data={"username": "itemuser", "password": "1234"},
    )

    token = login.json()["access_token"]

    response = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Notebook", "description": "Gaming", "cant": 1},
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
        data={"username": "sumuser", "password": "1234"},
    )

    token = login.json()["access_token"]

    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Mouse", "description": "Gamer", "cant": 2},
    )

    response = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Mouse", "description": "Gamer", "cant": 3},
    )

    data = response.json()

    assert data["cant"] == 5

def test_list_items(client):
    """Listar items devuelve solo los del usuario."""
    token = crear_usuario_y_login(client, "listuser", "list@test.com")
 
    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Item A", "cant": 1},
    )
    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Item B", "cant": 2},
    )
 
    response = client.get("/items/", headers={"Authorization": f"Bearer {token}"})
 
    assert response.status_code == 200
    titles = [i["title"] for i in response.json()]
    assert "Item A" in titles
    assert "Item B" in titles
 
 
def test_list_items_solo_propios(client):
    """Un usuario no ve los items de otro usuario."""
    token_a = crear_usuario_y_login(client, "usera", "usera@test.com")
    token_b = crear_usuario_y_login(client, "userb", "userb@test.com")
 
    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"title": "Item de A", "cant": 1},
    )
 
    response = client.get("/items/", headers={"Authorization": f"Bearer {token_b}"})
 
    assert response.status_code == 200
    assert response.json() == []
 
 
 
def test_delete_item_propio(client):
    """Un usuario puede eliminar su propio item."""
    token = crear_usuario_y_login(client, "delowner", "delowner@test.com")
 
    item = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Borrable", "cant": 1},
    ).json()
 
    response = client.delete(
        f"/items/{item['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 200
    assert response.json()["ok"] is True
 
 
def test_delete_item_ajeno(client):
    """Un usuario no puede eliminar el item de otro."""
    token_owner = crear_usuario_y_login(client, "owner", "owner@test.com")
    token_otro = crear_usuario_y_login(client, "otro", "otro@test.com")
 
    item = client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token_owner}"},
        json={"title": "No tuyo", "cant": 1},
    ).json()
 
    response = client.delete(
        f"/items/{item['id']}",
        headers={"Authorization": f"Bearer {token_otro}"},
    )
 
    assert response.status_code == 403
 
 
def test_delete_item_inexistente(client):
    """Eliminar un item que no existe devuelve 404."""
    token = crear_usuario_y_login(client, "delnoex", "delnoex@test.com")
 
    response = client.delete(
        "/items/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 404


def test_count_items_usuario_inexistente(client):
    """Pedir el conteo de un usuario que no existe devuelve 404."""
    token = crear_usuario_y_login(client, "checkerx", "checkerx@test.com")
 
    response = client.get(
        "/users/9999/items/count",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 404
