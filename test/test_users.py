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
        data={"username": "admin_delete", "password": "1234"},
    )

    token = login.json()["access_token"]

    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400



 
def test_get_user_por_id(client):
    """Obtener un usuario específico por ID devuelve sus datos."""
    token = crear_usuario_y_login(client, "getuser", "getuser@test.com")
 
    users = client.get("/users/", headers={"Authorization": f"Bearer {token}"}).json()
    user_id = users[0]["id"]
 
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "getuser"
 
 
def test_get_user_inexistente(client):
    """Obtener un usuario que no existe devuelve 404."""
    token = crear_usuario_y_login(client, "getuser2", "getuser2@test.com")
 
    response = client.get(
        "/users/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 404
 
 

 
def test_update_user(client):
    """Actualizar el nombre de un usuario devuelve los datos actualizados."""
    token = crear_usuario_y_login(client, "patchuser", "patch@test.com")
    users = client.get("/users/", headers={"Authorization": f"Bearer {token}"}).json()
    user_id = users[0]["id"]
 
    response = client.patch(
        f"/users/{user_id}",
        json={"full_name": "Nombre Actualizado"},
    )
 
    assert response.status_code == 200
    assert response.json()["full_name"] == "Nombre Actualizado"
 
 
def test_update_user_inexistente(client):
    """Actualizar un usuario que no existe devuelve 404."""
    response = client.patch(
        "/users/9999",
        json={"full_name": "Nadie"},
    )
 
    assert response.status_code == 404
 
 

 
def test_user_sin_rol_admin_no_puede_borrar(client):
    """Un usuario con rol 'user' no puede eliminar usuarios."""
    crear_usuario_y_login(client, "victima", "victima@test.com")
    token_user = crear_usuario_y_login(client, "atacante", "atacante@test.com")
 
    users = client.get("/users/", headers={"Authorization": f"Bearer {token_user}"}).json()
    victima_id = next(u["id"] for u in users if u["username"] == "victima")
 
    response = client.delete(
        f"/users/{victima_id}",
        headers={"Authorization": f"Bearer {token_user}"},
    )
 
    assert response.status_code == 403
 
 
def test_admin_puede_borrar_otro_usuario(client):
    """Un admin puede eliminar a otro usuario."""
    token_admin = crear_usuario_y_login(
        client, "adminborrar", "adminborrar@test.com", role="admin"
    )
    crear_usuario_y_login(client, "objetivo", "objetivo@test.com")
 
    users = client.get(
        "/users/", headers={"Authorization": f"Bearer {token_admin}"}
    ).json()
    objetivo_id = next(u["id"] for u in users if u["username"] == "objetivo")
 
    response = client.delete(
        f"/users/{objetivo_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
 
    assert response.status_code == 200
    assert response.json()["ok"] is True
 
def test_count_items_usuario(client):
    """Devuelve el conteo correcto de items diferentes de un usuario."""
    token = crear_usuario_y_login(client, "countuser", "count@test.com")
 
    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "X", "cant": 1},
    )
    client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Y", "cant": 1},
    )
 
    users = client.get("/users/", headers={"Authorization": f"Bearer {token}"}).json()
    user_id = users[0]["id"]
 
    response = client.get(
        f"/users/{user_id}/items/count",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 2
    assert data["user_id"] == user_id
 
 
def test_count_items_usuario_sin_items(client):
    """Un usuario sin items devuelve  0."""
    token = crear_usuario_y_login(client, "sinItems", "sinitems@test.com")
    users = client.get("/users/", headers={"Authorization": f"Bearer {token}"}).json()
    user_id = users[0]["id"]
 
    response = client.get(
        f"/users/{user_id}/items/count",
        headers={"Authorization": f"Bearer {token}"},
    )
 
    assert response.status_code == 200
    assert response.json()["item_count"] == 0
 