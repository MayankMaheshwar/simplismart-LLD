import pytest
from fastapi.testclient import TestClient
from main import app
from app.schemas.organization import Organization, OrganizationCreate
from app.models.user import User
from unittest.mock import patch
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture
def mock_db():
    with patch("app.core.deps.get_db") as mock_db:
        yield mock_db


@pytest.fixture
def mock_user():
    return User(
        id=1, username="testuser", email="testuser@example.com", organization=None
    )


@pytest.fixture
def organization_in():
    return OrganizationCreate(name="Test Organization")


@pytest.fixture
def mock_organization():
    return Organization(id=1, name="Test Organization", invite_code="1234567890")


def test_create_organization(mock_db, mock_user, organization_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        with patch("app.utils.generate_random_string", return_value="1234567890"):
            with patch("app.crud.create_organization") as mock_create_organization:
                mock_create_organization.return_value = mock_organization

                mock_db.add.return_value = None
                mock_db.commit.return_value = None

                response = client.post("/organizations/", json=organization_in.dict())

                assert response.status_code == 200
                assert response.json()["name"] == mock_organization.name
                assert response.json()["invite_code"] == mock_organization.invite_code


def test_create_organization_user_has_org(mock_db, mock_user):
    mock_user.organization = mock_organization
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        response = client.post("/organizations/", json={"name": "Test Organization"})

    assert response.status_code == 400
    assert response.json()["detail"] == "User already belongs to an organization"


def test_join_organization(mock_db, mock_user, mock_organization):
    mock_user.organization = None
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        with patch(
            "app.crud.get_organization_by_invite_code", return_value=mock_organization
        ):
            mock_db.add.return_value = None
            mock_db.commit.return_value = None

            response = client.post(
                f"/organizations/{mock_organization.invite_code}/join"
            )

            assert response.status_code == 200
            assert response.json()["message"] == "Successfully joined organization"


def test_join_organization_invalid_invite_code(mock_db, mock_user):
    mock_user.organization = None
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        with patch("app.crud.get_organization_by_invite_code", return_value=None):
            mock_db.add.return_value = None
            mock_db.commit.return_value = None

            response = client.post("/organizations/invalid_invite_code/join")

            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid invite code"


def test_join_organization_user_has_org(mock_db, mock_user, mock_organization):
    mock_user.organization = mock_organization
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        response = client.post(f"/organizations/{mock_organization.invite_code}/join")

    assert response.status_code == 400
    assert response.json()["detail"] == "User already belongs to an organization"
