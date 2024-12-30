from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core import deps
from app.schemas.organization import Organization, OrganizationCreate
from app.utils import generate_random_string
from app import crud

router = APIRouter()


@router.post("/", response_model=Organization)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Creates a new organization with a random invite code.

    Raises:
        HTTPException: 400 - User already has an organization
    """

    if current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to an organization",
        )

    # Generate a random, unique invite code
    invite_code = generate_random_string(length=10)
    while crud.get_organization_by_invite_code(db, invite_code):
        invite_code = generate_random_string(length=10)

    organization = crud.create_organization(
        db, organization_in, invite_code=invite_code
    )

    current_user.organization = organization
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return organization


@router.post("/{invite_code}/join")
def join_organization(
    *,
    db: Session = Depends(deps.get_db),
    invite_code: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Allows a user to join an organization using an invite code.

    Raises:
        HTTPException: 400 - User already has an organization, Invalid invite code
    """

    if current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to an organization",
        )

    organization = crud.get_organization_by_invite_code(db, invite_code)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite code"
        )

    current_user.organization = organization
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Successfully joined organization"}
