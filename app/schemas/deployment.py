from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.deployment import DeploymentStatus


class DeploymentBase(BaseModel):
    name: str
    docker_image: str
    cpu_required: float
    ram_required: float
    gpu_required: float
    priority: int = 0


class DeploymentCreate(DeploymentBase):
    cluster_id: int
    required_time: int


class DeploymentUpdate(DeploymentBase):
    pass


class Deployment(DeploymentBase):
    cluster_id: int
    status: DeploymentStatus

    class Config:
        from_attributes = True
