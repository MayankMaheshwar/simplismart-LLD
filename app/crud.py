import uuid
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.cluster import Cluster


def create_organization(
    db: Session, organization_in: OrganizationCreate, invite_code: str
) -> Organization:
    """Creates a new organization record in the database."""
    organization = Organization(name=organization_in.name, invite_code=invite_code)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def get_organization_by_invite_code(db: Session, invite_code: str) -> Organization:
    """Retrieves an organization by its invite code."""
    return (
        db.query(Organization).filter(Organization.invite_code == invite_code).first()
    )


def get_organization_by_id(db: Session, id: int) -> Organization | None:
    """
    Retrieves an organization by its ID from the database.

    Args:
        db: SQLAlchemy database session.
        id: The ID of the organization to retrieve.

    Returns:
        The Organization object if found, otherwise None.
    """
    return db.query(Organization).filter(Organization.id == id).first()


def create_cluster(db: Session, cluster: Cluster) -> Cluster:
    """
    Create a new cluster in the database.
    """
    new_cluster = Cluster(
        name=cluster.name,
        organization_id=cluster.organization_id,
        cpu_limit=cluster.cpu_limit,
        ram_limit=cluster.ram_limit,
        gpu_limit=cluster.gpu_limit,
        cpu_available=cluster.cpu_limit,
        ram_available=cluster.ram_limit,
        gpu_available=cluster.gpu_limit,
    )
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)
    return new_cluster


def get_clusters_by_organization(db: Session, organization_id: int) -> List[Cluster]:
    """
    Retrieve all clusters belonging to a specific organization.
    """
    clusters = (
        db.query(Cluster).filter(Cluster.organization_id == organization_id).all()
    )
    if not clusters:
        raise HTTPException(
            status_code=404, detail="No clusters found for the organization"
        )
    return clusters
