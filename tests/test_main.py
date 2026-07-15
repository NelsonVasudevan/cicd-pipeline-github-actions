import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task():
    response = client.post("/tasks", json={"title": "Write tests"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["done"] is False


def test_created_task_appears_in_list():
    client.post("/tasks", json={"title": "Second task"})
    response = client.get("/tasks")
    titles = [task["title"] for task in response.json()]
    assert "Second task" in titles
