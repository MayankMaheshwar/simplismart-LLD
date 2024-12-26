from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core import deps, security
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str,
    password: str,
    db: Session = Depends(deps.get_db),
):
    """
    TODO: Implement login endpoint using session
    Example:
    - Find user by username
    - Verify password
    - Set user_id in session
    - Return success message
    """
    pass


@router.post("/register", response_model=User)
async def register(*, db: Session = Depends(deps.get_db), user_in: UserCreate):
    """
    TODO: Implement user registration
    Example:
    - Check if username/email already exists
    - Hash password
    - Create user in database
    - Return user data
    """
    pass


@router.post("/logout")
async def logout(request: Request):
    """
    TODO: Implement logout endpoint
    Example:
    request.session.clear()
    return {"message": "Successfully logged out"}
    """
    pass
