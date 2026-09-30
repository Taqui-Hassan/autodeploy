import pytest
from app.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    return app.test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_add_and_list(client):
    res = client.post("/api/tasks", json={"title": "learn docker"})
    assert res.status_code == 201
    tasks = client.get("/api/tasks").get_json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "learn docker"
    assert tasks[0]["done"] == 0


def test_empty_title_rejected(client):
    res = client.post("/api/tasks", json={"title": "  "})
    assert res.status_code == 400


def test_toggle(client):
    task_id = client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    client.patch(f"/api/tasks/{task_id}/toggle")
    assert client.get("/api/tasks").get_json()[0]["done"] == 1
    client.patch(f"/api/tasks/{task_id}/toggle")
    assert client.get("/api/tasks").get_json()[0]["done"] == 0


def test_delete(client):
    task_id = client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    assert client.delete(f"/api/tasks/{task_id}").status_code == 200
    assert client.get("/api/tasks").get_json() == []


def test_missing_task_returns_404(client):
    assert client.delete("/api/tasks/999").status_code == 404
    assert client.patch("/api/tasks/999/toggle").status_code == 404
