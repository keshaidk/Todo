"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def valid_init_data():
    """Create valid init data for tests"""
    import hashlib
    import hmac
    import json
    from config import settings
    
    user_data = json.dumps({"id": 123456, "first_name": "Test"})
    params = {
        "user": user_data,
        "auth_date": "1700000000",
    }
    
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    params["hash"] = hash_value
    return "&".join(f"{k}={v}" for k, v in params.items())


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task_without_auth(client):
    """Test creating task without authentication"""
    response = client.post(
        "/api/tasks",
        json={"text": "Test task"}
    )
    assert response.status_code == 422  # Validation error (missing header)


def test_get_tasks_without_auth(client):
    """Test getting tasks without authentication"""
    response = client.get("/api/tasks")
    assert response.status_code == 422


def test_create_task(client, valid_init_data):
    """Test creating a task"""
    response = client.post(
        "/api/tasks",
        json={"text": "Test task"},
        headers={"X-Init-Data": valid_init_data}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test task"
    assert data["completed"] is False
    assert "id" in data


def test_get_tasks(client, valid_init_data):
    """Test getting tasks"""
    # Create a task first
    create_response = client.post(
        "/api/tasks",
        json={"text": "Task 1"},
        headers={"X-Init-Data": valid_init_data}
    )
    assert create_response.status_code == 201
    
    # Get tasks
    response = client.get(
        "/api/tasks",
        headers={"X-Init-Data": valid_init_data}
    )
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 1


def test_update_task(client, valid_init_data):
    """Test updating a task"""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"text": "Original text"},
        headers={"X-Init-Data": valid_init_data}
    )
    task_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"text": "Updated text"},
        headers={"X-Init-Data": valid_init_data}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated text"


def test_complete_task(client, valid_init_data):
    """Test completing a task"""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"text": "Task to complete"},
        headers={"X-Init-Data": valid_init_data}
    )
    task_id = create_response.json()["id"]
    
    # Complete it
    response = client.post(
        f"/api/tasks/{task_id}/complete",
        headers={"X-Init-Data": valid_init_data}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True


def test_delete_task(client, valid_init_data):
    """Test deleting a task"""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"text": "Task to delete"},
        headers={"X-Init-Data": valid_init_data}
    )
    task_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"X-Init-Data": valid_init_data}
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"X-Init-Data": valid_init_data}
    )
    assert get_response.status_code == 404
