from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core import deps
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/login")
async def login(
    request: Request,
    username: str,
    password: str,
    db: Session = Depends(deps.get_db),
):
    """
    Performs login using username and password.

    Raises:
        HTTPException: 400 - Username or password is incorrect
    """

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    hashed_password = str(user.hashed_password)

    is_valid_password = verify_password(password, hashed_password)
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    request.session["user_id"] = user.id

    return {"message": "Successfully logged in"}


@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    """
    Registers a new user with username, email, and password.

    Raises:
        HTTPException: 400 - Username or email already exists
    """

    try:
        existing_user = (
            db.query(UserModel)
            .filter(
                (UserModel.username == user_in.username)
                | (UserModel.email == user_in.email)
            )
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )
        hashed_password: str = get_password_hash(user_in.password)
        user = UserModel(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    except Exception as e:
        print(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/logout")
async def logout(request: Request):
    """
    Logs out the current user by clearing the session.
    """

    request.session.clear()
    return {"message": "Successfully logged out"}
