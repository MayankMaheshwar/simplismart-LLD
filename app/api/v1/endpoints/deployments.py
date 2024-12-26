from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Deployment)
def create_deployment(
    *,
    db: Session = Depends(deps.get_db),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement deployment creation and scheduling
    """
    pass


@router.get("/", response_model=List[Deployment])
def list_deployments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    TODO: Implement deployment listing
    """
    pass
