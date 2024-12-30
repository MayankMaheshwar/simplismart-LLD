import pytest
from fastapi.testclient import TestClient
from main import app
from app.schemas.cluster import Cluster
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
        id=1, username="testuser", email="testuser@example.com", organization_id=1
    )


@pytest.fixture
def cluster_data():
    return {"name": "Test Cluster", "cpu_limit": 16, "ram_limit": 32, "gpu_limit": 4}


@pytest.fixture
def cluster_in(cluster_data):
    return Cluster(**cluster_data)


def test_create_cluster(mock_db, mock_user, cluster_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = (
            None
        )
        with patch("app.crud.create_cluster") as mock_create_cluster:
            mock_create_cluster.return_value = cluster_in

            response = client.post("/clusters/", json=cluster_in.dict())

            assert response.status_code == 200
            assert response.json()["name"] == cluster_in.name
            assert response.json()["cpu_available"] == cluster_in.cpu_limit
            assert response.json()["ram_available"] == cluster_in.ram_limit
            assert response.json()["gpu_available"] == cluster_in.gpu_limit


def test_create_cluster_no_org(mock_db, cluster_in):
    with patch(
        "app.core.deps.get_current_user",
        return_value=User(id=1, username="testuser", email="testuser@example.com"),
    ):
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = client.post("/clusters/", json=cluster_in.dict())

    assert response.status_code == 400
    assert response.json()["detail"] == "User does not belong to any organization"


def test_list_clusters(mock_db, mock_user, cluster_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        mock_db.return_value.query.return_value.filter.return_value.all.return_value = [
            cluster_in
        ]
        with patch("app.crud.get_clusters_by_organization") as mock_get_clusters:
            mock_get_clusters.return_value = [cluster_in]

            response = client.get("/clusters/")

            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["name"] == cluster_in.name
            assert response.json()[0]["cpu_available"] == cluster_in.cpu_limit
            assert response.json()[0]["ram_available"] == cluster_in.ram_limit
            assert response.json()[0]["gpu_available"] == cluster_in.gpu_limit


def test_list_clusters_no_org(mock_db):
    with patch(
        "app.core.deps.get_current_user",
        return_value=User(id=1, username="testuser", email="testuser@example.com"),
    ):
        mock_db.return_value.query.return_value.filter.return_value.all.return_value = (
            []
        )

        response = client.get("/clusters/")

    assert response.status_code == 400
    assert response.json()["detail"] == "User does not belong to any organization"
