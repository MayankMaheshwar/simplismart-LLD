from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core import deps
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.deployment import Deployment as DeploymentModel, DeploymentStatus
from app.models.user import User
from app.models.cluster import Cluster
from sqlalchemy import and_


router = APIRouter()


def schedule_deployment(
    db: Session, deployment_in: DeploymentCreate
) -> DeploymentModel:
    """
    Schedules a deployment by checking resource availability and preempting lower-priority deployments if needed.
    """

    # Query the target cluster
    cluster = db.query(Cluster).filter(Cluster.id == deployment_in.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Check if there are sufficient resources in the cluster
    if (
        cluster.cpu_available < deployment_in.cpu_required
        or cluster.ram_available < deployment_in.ram_required
        or cluster.gpu_available < deployment_in.gpu_required
    ):
        # Fetch lower-priority running deployments for preemption
        lower_priority_deployments = (
            db.query(DeploymentModel)
            .filter(
                and_(
                    DeploymentModel.cluster_id == cluster.id,
                    DeploymentModel.priority < deployment_in.priority,
                    DeploymentModel.status == DeploymentStatus.RUNNING,
                )
            )
            .order_by(
                DeploymentModel.priority.asc()
            )  # Ascending priority (lower values first)
            .all()
        )

        # Attempt to free resources by preempting lower-priority deployments
        for dep in lower_priority_deployments:
            # Free resources from the lower-priority deployment
            cluster.cpu_available += dep.cpu_required
            cluster.ram_available += dep.ram_required
            cluster.gpu_available += dep.gpu_required

            # Mark the lower-priority deployment as FAILED
            dep.status = DeploymentStatus.FAILED
            db.add(dep)

            # Check if the freed resources are now sufficient
            if (
                cluster.cpu_available >= deployment_in.cpu_required
                and cluster.ram_available >= deployment_in.ram_required
                and cluster.gpu_available >= deployment_in.gpu_required
            ):
                break
        else:
            # If no sufficient resources can be freed, return an error
            raise HTTPException(
                status_code=400, detail="Insufficient resources even after preemption"
            )

    # Allocate resources for the new deployment
    cluster.cpu_available -= deployment_in.cpu_required
    cluster.ram_available -= deployment_in.ram_required
    cluster.gpu_available -= deployment_in.gpu_required

    # Retrieve the deployment instance created in `create_deployment`
    deployment = (
        db.query(DeploymentModel)
        .filter(
            DeploymentModel.name == deployment_in.name,
            DeploymentModel.cluster_id == deployment_in.cluster_id,
            DeploymentModel.status == DeploymentStatus.PENDING,
        )
        .first()
    )

    if not deployment:
        raise HTTPException(
            status_code=400, detail="Pending deployment record not found"
        )

    # Update the deployment status to RUNNING
    deployment.status = DeploymentStatus.RUNNING
    db.add(deployment)

    # Save the changes to the database
    db.add(cluster)
    db.commit()
    db.refresh(deployment)

    return deployment


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
    # Check if the user has access to the cluster
    cluster = db.query(Cluster).filter(Cluster.id == deployment_in.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Create deployment instance
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

    # Schedule the deployment
    schedule_deployment(db=db, deployment_in=deployment_in)
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
    deployments = db.query(DeploymentModel).all()
    return deployments
