import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.user import User as UserModel
from app.core.security import get_password_hash
from app.schemas.user import UserCreate
from unittest.mock import patch

# Initialize TestClient
client = TestClient(app)


@pytest.fixture
def mock_db():

    mock_db = patch("app.core.deps.get_db").start()
    yield mock_db
    patch("app.core.deps.get_db").stop()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
    }


@pytest.fixture
def user_in(user_data):
    return UserCreate(**user_data)


@pytest.fixture
def user_model(user_data):
    hashed_password = get_password_hash(user_data["password"])
    return UserModel(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
    )


def test_register(mock_db, user_in, user_model):
    mock_db.query().filter().first.return_value = None

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = user_model

    response = client.post("/register", json=user_in.dict())

    assert response.status_code == 200
    assert response.json()["username"] == user_in.username
    assert response.json()["email"] == user_in.email


def test_register_existing_user(mock_db, user_in, user_model):
    mock_db.query().filter().first.return_value = user_model

    response = client.post("/register", json=user_in.dict())

    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email already exists"


def test_login(mock_db, user_in, user_model):
    mock_db.query().filter().first.return_value = user_model

    with patch("app.core.security.verify_password") as mock_verify_password:
        mock_verify_password.return_value = True

        response = client.post(
            "/login", data={"username": user_in.username, "password": user_in.password}
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged in"


def test_login_invalid_credentials(mock_db, user_in, user_model):
    mock_db.query().filter().first.return_value = user_model

    with patch("app.core.security.verify_password") as mock_verify_password:
        mock_verify_password.return_value = False

        response = client.post(
            "/login", data={"username": user_in.username, "password": "wrongpassword"}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


def test_logout(mock_db):
    with patch("app.main.Request") as mock_request:
        mock_request.session.clear = lambda: None

        response = client.post("/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
