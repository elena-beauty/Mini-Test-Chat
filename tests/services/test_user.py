import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.user import (
    verify_password,
    get_password_hash,
    create_access_token,
    signup_user,
    login_user,
    create_user,
    get_user_by_id,
    get_all_users,
    get_current_user,
)
from model.user import User
from datetime import timedelta

@pytest.fixture
def mock_db():
    """
    Fixture to create a mocked database session.
    """
    return MagicMock(spec=Session)

def test_verify_password():
    """
    Test the verify_password function.
    """
    hashed_password = get_password_hash("test_password")
    assert verify_password("test_password", hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False

def test_get_password_hash():
    """
    Test the get_password_hash function.
    """
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert isinstance(hashed_password, str)

def test_create_access_token():
    """
    Test the create_access_token function.
    """
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)

    expires_delta = timedelta(minutes=10)
    token_with_expiration = create_access_token(data, expires_delta)
    assert isinstance(token_with_expiration, str)

def test_signup_user(mock_db):
    """
    Test the signup_user function.
    """
    mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    request = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "test_password",
        "gender": "male",
    }

    result = signup_user(mock_db, request)
    assert result["message"] == "User created successfully"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    mock_db.query.return_value.filter.return_value.first.return_value = User(email="test@example.com")
    with pytest.raises(HTTPException) as excinfo:
        signup_user(mock_db, request)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Email already registered"

def test_login_user(mock_db):
    """
    Test the login_user function.
    """
    mock_user = User(email="test@example.com", password=get_password_hash("test_password"))
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    request = {
        "email": "test@example.com",
        "password": "test_password",
    }

    result = login_user(mock_db, request)
    assert "access_token" in result
    assert result["token_type"] == "bearer"

    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        login_user(mock_db, request)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid email or password"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    request["password"] = "wrong_password"
    with pytest.raises(HTTPException) as excinfo:
        login_user(mock_db, request)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid email or password"

def test_create_user(mock_db):
    """
    Test the create_user function.
    """
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    name = "Test User"
    email = "test@example.com"
    gender = "male"

    result = create_user(mock_db, name, email, gender)
    assert result.name == name
    assert result.email == email
    assert result.gender == gender
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_user_by_id(mock_db):
    """
    Test the get_user_by_id function.
    """
    mock_user = User(id=1, name="Test User", email="test@example.com", gender="male")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    result = get_user_by_id(mock_db, 1)
    assert result.id == 1
    assert result.name == "Test User"
    assert result.email == "test@example.com"
    assert result.gender == "male"

def test_get_all_users(mock_db):
    """
    Test the get_all_users function.
    """
    mock_users = [
        User(id=1, name="Test User 1", email="test1@example.com", gender="male"),
        User(id=2, name="Test User 2", email="test2@example.com", gender="female"),
    ]
    mock_db.query.return_value.all.return_value = mock_users

    result = get_all_users(mock_db)
    assert len(result) == 2
    assert result[0].name == "Test User 1"
    assert result[1].name == "Test User 2"

def test_get_current_user(mock_db):
    """
    Test the get_current_user function.
    """
    mock_user = User(email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    token = create_access_token({"sub": "test@example.com"})
    result = get_current_user(token, mock_db)
    assert result.email == "test@example.com"

    with pytest.raises(HTTPException) as excinfo:
        get_current_user("", mock_db)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Missing token"

    with pytest.raises(HTTPException) as excinfo:
        get_current_user("invalid_token", mock_db)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"

    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token, mock_db)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "User not found"
