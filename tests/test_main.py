import pytest
from fastapi.testclient import TestClient
from main import app 
from unittest.mock import MagicMock, patch

# Create a TestClient instance for testing
client = TestClient(app)

# Mock database dependency
@pytest.fixture
def mock_db():
    return MagicMock()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}


def test_signup():
    with patch("main.get_db") as mock_get_db:
        mock_db = mock_get_db.return_value
        mock_db.signup_user.return_value = {
            "id": 1,
            "name": "John Doe",
            "email": "john11111@example.com",
            "gender": "male"
        }

        response = client.post(
            "/signup/",
            json={
                "name": "John Doe",
                "email": "john11111@example.com",
                "password": "password123",
                "gender": "male"
            },
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json() == {
            "id": 1,
            "name": "John Doe",
            "email": "john11111@example.com",
            "gender": "male"
        }

def test_login():
    with patch("main.get_db") as mock_get_db:
        mock_db = mock_get_db.return_value
        mock_db.login_user.return_value = {"access_token": "mock_token"}

        response = client.post(
            "/login/",
            json={"email": "john@example.com", "password": "password123"},
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json() == {"access_token": "mock_token"}

def test_create_message(mock_db):
    mock_db.add_message.return_value = {"id": 1, "user_id": 1, "type": "text", "content": "Hello"}
    response = client.post(
        "/messages/",
        params={"user_id": 1, "message_type": "text", "content": "Hello"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "user_id": 1, "type": "text", "content": "Hello"}

def test_retrieve_messages(mock_db):
    mock_db.get_messages.return_value = [
        {"id": 1, "user_id": 1, "type": "text", "content": "Hello"},
        {"id": 2, "user_id": 1, "type": "text", "content": "Hi"},
    ]
    response = client.get("/messages/", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 2

# Test current user info endpoint
def test_get_current_user_info(mock_db):
    mock_db.get_current_user.return_value = {"id": 1, "name": "John Doe", "email": "john@example.com"}
    response = client.get("/me", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    assert response.json() == {"user_id": 1, "name": "John Doe", "email": "john@example.com"}
