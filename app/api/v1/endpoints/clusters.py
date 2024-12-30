from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.cluster import Cluster
from app.models.user import User
from app.crud import (
    create_cluster as crud_create_cluster,
    get_clusters_by_organization,
)

router = APIRouter()


@router.post("/", response_model=Cluster)
def create_cluster(
    *,
    db: Session = Depends(deps.get_db),
    cluster_in: Cluster,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new cluster for the current user's organization.
    """
    if not hasattr(current_user, "organization_id"):
        raise HTTPException(
            status_code=400, detail="User does not belong to any organization"
        )

    updated_cluster_in = cluster_in.model_copy(
        update={
            "organization_id": current_user.organization_id,
            "cpu_available": cluster_in.cpu_limit,
            "ram_available": cluster_in.ram_limit,
            "gpu_available": cluster_in.gpu_limit,
        }
    )

    return crud_create_cluster(db=db, cluster=updated_cluster_in)


@router.get("/", response_model=List[Cluster])
def list_clusters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List all clusters belonging to the current user's organization.
    """
    if not hasattr(current_user, "organization_id"):
        raise HTTPException(
            status_code=400, detail="User does not belong to any organization"
        )

    return get_clusters_by_organization(
        db=db, organization_id=current_user.organization_id
    )
