from pydantic import BaseModel


class ClusterBase(BaseModel):
    name: str
    cpu_limit: float
    ram_limit: float
    gpu_limit: float


class ClusterCreate(ClusterBase):
    organization_id: int


class ClusterUpdate(ClusterBase):
    pass


class Cluster(ClusterBase):
    organization_id: int
    cpu_available: float
    ram_available: float
    gpu_available: float

    class Config:
        from_attributes = True
