from fastapi import APIRouter, Depends, HTTPException
import redis
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core import deps
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.deployment import Deployment as DeploymentModel, DeploymentStatus
from app.models.user import User
from app.models.cluster import Cluster


router = APIRouter()
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


@router.post("/", response_model=Deployment)
def create_deployment(
    *,
    db: Session = Depends(deps.get_db),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new deployment and schedule it.
    """
    cluster = db.query(Cluster).filter(Cluster.id == deployment_in.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    if cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="User does not have access to this organization's cluster",
        )

    if (
        cluster.cpu_available < deployment_in.cpu_required
        or cluster.ram_available < deployment_in.ram_required
        or cluster.gpu_available < deployment_in.gpu_required
    ):
        raise HTTPException(
            status_code=400, detail="Insufficient resources to create deployment"
        )

    deployment = DeploymentModel(
        **deployment_in.dict(), status=DeploymentStatus.PENDING
    )
    db.add(deployment)
    try:
        db.commit()
        db.refresh(deployment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Deployment creation failed")

    redis_key = f"org:{current_user.organization_id}:deployments"
    redis_data = {
        "id": deployment.id,
        "cluster_id": deployment_in.cluster_id,
        "cpu_required": deployment_in.cpu_required,
        "ram_required": deployment_in.ram_required,
        "gpu_required": deployment_in.gpu_required,
        "status": deployment.status,
        "created_at": str(deployment.created_at),
    }

    redis_client.rpush(redis_key, str(deployment.id))

    redis_client.hmset(f"deployment:{deployment.id}", redis_data)

    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    return deployment


@router.get("/", response_model=List[Deployment])
def list_deployments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List all deployments for the user's organization.
    """
    redis_key = f"org:{current_user.organization_id}:deployments"

    deployment_ids = redis_client.lrange(redis_key, 0, -1)

    if deployment_ids:
        deployments = []
        for deployment_id in deployment_ids:
            deployment_data = redis_client.hgetall(f"deployment:{deployment_id}")
            if deployment_data:
                deployments.append(Deployment(**deployment_data))
        return deployments

    deployments = (
        db.query(DeploymentModel)
        .filter(DeploymentModel.organization_id == current_user.organization_id)
        .all()
    )

    for deployment in deployments:
        redis_client.rpush(redis_key, str(deployment.id))
        redis_client.hmset(
            f"deployment:{deployment.id}",
            {
                "id": deployment.id,
                "cluster_id": deployment.cluster_id,
                "cpu_required": deployment.cpu_required,
                "ram_required": deployment.ram_required,
                "gpu_required": deployment.gpu_required,
                "status": deployment.status,
                "created_at": str(deployment.created_at),
            },
        )

    return deployments
