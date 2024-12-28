from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies the provided plain password against the given hashed password.

    Args:
        plain_password: The plain-text password to be verified.
        hashed_password: The previously hashed password to compare against.

    Returns:
        True if the plain password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes the given password using the bcrypt algorithm.

    Args:
        password: The plain-text password to be hashed.

    Returns:
        The hashed password as a string.
    """
    return pwd_context.hash(password)
