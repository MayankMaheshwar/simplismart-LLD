from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    TODO: Implement password verification using bcrypt
    Example:
    return pwd_context.verify(plain_password, hashed_password)
    """
    pass


def get_password_hash(password: str) -> str:
    """
    TODO: Implement password hashing using bcrypt
    Example:
    return pwd_context.hash(password)
    """
    pass
