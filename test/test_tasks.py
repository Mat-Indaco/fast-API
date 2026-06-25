from datetime import date, timedelta


def login(client, username, password="1234"):
    r = client.post("/login", data={"username": username, "password": password})
    return r.json()["access_token"]


def register_and_login(client, username, email, password="1234"):
    client.post(
        "/users/",
        json={
            "username": username,
            "email": email,
            "full_name": username,
            "password": password,
        },
    )
    return login(client, username, password)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tasks CRUD
# ---------------------------------------------------------------------------

def test_create_task(client):
    token = register_and_login(client, "taskuser", "task@test.com")
    r = client.post(
        "/tasks/",
        headers=auth(token),
        json={"title": "Mi primera tarea", "priority": "high"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Mi primera tarea"
    assert data["status"] == "pending"
    assert data["priority"] == "high"


def test_list_tasks_solo_propias(client):
    token_a = register_and_login(client, "usera_t", "usera_t@test.com")
    token_b = register_and_login(client, "userb_t", "userb_t@test.com")

    client.post("/tasks/", headers=auth(token_a), json={"title": "Tarea de A"})

    r = client.get("/tasks/", headers=auth(token_b))
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_status(client):
    token = register_and_login(client, "filteruser", "filter@test.com")
    client.post("/tasks/", headers=auth(token), json={"title": "Pendiente", "status": "pending"})
    client.post("/tasks/", headers=auth(token), json={"title": "En progreso", "status": "in_progress"})

    r = client.get("/tasks/?status=pending", headers=auth(token))
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert "Pendiente" in titles
    assert "En progreso" not in titles


def test_list_tasks_filter_priority(client):
    token = register_and_login(client, "priouser", "prio@test.com")
    client.post("/tasks/", headers=auth(token), json={"title": "Alta", "priority": "high"})
    client.post("/tasks/", headers=auth(token), json={"title": "Baja", "priority": "low"})

    r = client.get("/tasks/?priority=high", headers=auth(token))
    titles = [t["title"] for t in r.json()]
    assert "Alta" in titles
    assert "Baja" not in titles


def test_list_tasks_search(client):
    token = register_and_login(client, "searchuser", "search@test.com")
    client.post("/tasks/", headers=auth(token), json={"title": "Deploy en producción"})
    client.post("/tasks/", headers=auth(token), json={"title": "Escribir documentación"})

    r = client.get("/tasks/?search=deploy", headers=auth(token))
    titles = [t["title"] for t in r.json()]
    assert "Deploy en producción" in titles
    assert "Escribir documentación" not in titles


def test_get_task(client):
    token = register_and_login(client, "getuser", "get@test.com")
    created = client.post(
        "/tasks/", headers=auth(token), json={"title": "Tarea detalle"}
    ).json()

    r = client.get(f"/tasks/{created['id']}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["title"] == "Tarea detalle"


def test_get_task_ajena_403(client):
    token_a = register_and_login(client, "ownerget", "ownerget@test.com")
    token_b = register_and_login(client, "otroget", "otroget@test.com")

    task = client.post("/tasks/", headers=auth(token_a), json={"title": "Privada"}).json()
    r = client.get(f"/tasks/{task['id']}", headers=auth(token_b))
    assert r.status_code == 403


def test_update_task(client):
    token = register_and_login(client, "updateuser", "update@test.com")
    task = client.post(
        "/tasks/", headers=auth(token), json={"title": "Antes"}
    ).json()

    r = client.patch(
        f"/tasks/{task['id']}",
        headers=auth(token),
        json={"title": "Después", "status": "in_progress"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Después"
    assert data["status"] == "in_progress"


def test_delete_task(client):
    token = register_and_login(client, "deluser", "del@test.com")
    task = client.post("/tasks/", headers=auth(token), json={"title": "Borrable"}).json()

    r = client.delete(f"/tasks/{task['id']}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get(f"/tasks/{task['id']}", headers=auth(token))
    assert r2.status_code == 404


def test_delete_task_ajena_403(client):
    token_a = register_and_login(client, "ownerdel", "ownerdel@test.com")
    token_b = register_and_login(client, "otrodeluser", "otrodeluser@test.com")

    task = client.post("/tasks/", headers=auth(token_a), json={"title": "No tuya"}).json()
    r = client.delete(f"/tasks/{task['id']}", headers=auth(token_b))
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def test_stats(client):
    token = register_and_login(client, "statsuser", "stats@test.com")
    client.post("/tasks/", headers=auth(token), json={"title": "P1", "status": "pending"})
    client.post("/tasks/", headers=auth(token), json={"title": "P2", "status": "in_progress"})
    client.post("/tasks/", headers=auth(token), json={"title": "P3", "status": "done"})

    r = client.get("/tasks/stats", headers=auth(token))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert data["pending"] == 1
    assert data["in_progress"] == 1
    assert data["done"] == 1


def test_stats_overdue(client):
    token = register_and_login(client, "overdueuser", "overdue@test.com")
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    client.post(
        "/tasks/",
        headers=auth(token),
        json={"title": "Vencida", "due_date": yesterday, "status": "pending"},
    )
    client.post(
        "/tasks/",
        headers=auth(token),
        json={"title": "Hecha vencida", "due_date": yesterday, "status": "done"},
    )

    r = client.get("/tasks/stats", headers=auth(token))
    data = r.json()
    assert data["overdue"] == 1


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def test_create_category(client):
    token = register_and_login(client, "catuser", "cat@test.com")
    r = client.post(
        "/categories/",
        headers=auth(token),
        json={"name": "Trabajo", "color": "#6366f1"},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Trabajo"


def test_category_duplicada_409(client):
    token = register_and_login(client, "catdup", "catdup@test.com")
    client.post("/categories/", headers=auth(token), json={"name": "Dup"})
    r = client.post("/categories/", headers=auth(token), json={"name": "Dup"})
    assert r.status_code == 409


def test_list_categories(client):
    token = register_and_login(client, "listcat", "listcat@test.com")
    client.post("/categories/", headers=auth(token), json={"name": "A"})
    client.post("/categories/", headers=auth(token), json={"name": "B"})

    r = client.get("/categories/", headers=auth(token))
    names = [c["name"] for c in r.json()]
    assert "A" in names and "B" in names


def test_delete_category_desasocia_tasks(client):
    token = register_and_login(client, "catdel", "catdel@test.com")
    cat = client.post("/categories/", headers=auth(token), json={"name": "Borrable"}).json()
    task = client.post(
        "/tasks/",
        headers=auth(token),
        json={"title": "Con categoría", "category_id": cat["id"]},
    ).json()
    assert task["category_id"] == cat["id"]

    client.delete(f"/categories/{cat['id']}", headers=auth(token))

    r = client.get(f"/tasks/{task['id']}", headers=auth(token))
    assert r.json()["category_id"] is None
