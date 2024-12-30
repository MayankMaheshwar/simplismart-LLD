import pytest
from fastapi.testclient import TestClient
from main import app
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.user import User
from app.models.cluster import Cluster
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
def mock_cluster():
    return Cluster(
        id=1,
        name="Test Cluster",
        organization_id=1,
        cpu_available=16,
        ram_available=32,
        gpu_available=4,
    )


@pytest.fixture
def deployment_data():
    return {
        "cluster_id": 1,
        "cpu_required": 4,
        "ram_required": 8,
        "gpu_required": 1,
    }


@pytest.fixture
def deployment_in(deployment_data):
    return DeploymentCreate(**deployment_data)


def test_create_deployment(mock_db, mock_user, mock_cluster, deployment_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = (
            mock_cluster
        )
        with patch("app.crud.create_deployment") as mock_create_deployment:
            mock_create_deployment.return_value = Deployment(
                id=1, **deployment_in.dict(), status="PENDING"
            )

            response = client.post("/deployments/", json=deployment_in.dict())

            assert response.status_code == 200
            assert response.json()["cluster_id"] == deployment_in.cluster_id
            assert response.json()["cpu_required"] == deployment_in.cpu_required
            assert response.json()["ram_required"] == deployment_in.ram_required
            assert response.json()["gpu_required"] == deployment_in.gpu_required


def test_create_deployment_cluster_not_found(mock_db, mock_user, deployment_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = client.post("/deployments/", json=deployment_in.dict())

    assert response.status_code == 404
    assert response.json()["detail"] == "Cluster not found"


def test_list_deployments(mock_db, mock_user, deployment_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        redis_key = f"org:{mock_user.organization_id}:deployments"
        mock_db.return_value.query.return_value.filter.return_value.all.return_value = [
            deployment_in
        ]

        with patch("app.redis_client.lrange", return_value=[1]):
            with patch("app.redis_client.hgetall", return_value=deployment_in.dict()):
                response = client.get("/deployments/")

                assert response.status_code == 200
                assert len(response.json()) == 1
                assert response.json()[0]["cluster_id"] == deployment_in.cluster_id


def test_list_deployments_no_data(mock_db, mock_user, deployment_in):
    with patch("app.core.deps.get_current_user", return_value=mock_user):
        redis_key = f"org:{mock_user.organization_id}:deployments"
        mock_db.return_value.query.return_value.filter.return_value.all.return_value = [
            deployment_in
        ]

        with patch("app.redis_client.lrange", return_value=[]):
            response = client.get("/deployments/")

            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["cluster_id"] == deployment_in.cluster_id
