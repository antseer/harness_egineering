def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_task(client):
    resp = client.post("/api/v1/tasks/", json={"title": "Test task"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test task"
    assert data["status"] == "pending"


def test_list_tasks(client):
    client.post("/api/v1/tasks/", json={"title": "Task 1"})
    client.post("/api/v1/tasks/", json={"title": "Task 2"})
    resp = client.get("/api/v1/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_task(client):
    create_resp = client.post("/api/v1/tasks/", json={"title": "My task"})
    task_id = create_resp.json()["id"]
    resp = client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "My task"


def test_get_task_not_found(client):
    resp = client.get("/api/v1/tasks/999")
    assert resp.status_code == 404


def test_update_task(client):
    create_resp = client.post("/api/v1/tasks/", json={"title": "Old title"})
    task_id = create_resp.json()["id"]
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"title": "New title", "status": "done"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["status"] == "done"


def test_delete_task(client):
    create_resp = client.post("/api/v1/tasks/", json={"title": "To delete"})
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204
    resp = client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 404
