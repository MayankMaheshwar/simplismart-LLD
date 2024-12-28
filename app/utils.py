import string
import random


def generate_random_string(length: int = 10) -> str:
    """Generates a random alphanumeric string of the specified length."""
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))
