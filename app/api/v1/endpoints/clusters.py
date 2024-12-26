from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.cluster import Cluster, ClusterCreate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Cluster)
def create_cluster(
    *,
    db: Session = Depends(deps.get_db),
    cluster_in: ClusterCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement cluster creation
    """
    pass


@router.get("/", response_model=List[Cluster])
def list_clusters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    TODO: Implement cluster listing
    """
    pass
