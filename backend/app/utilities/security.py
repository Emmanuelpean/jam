import hashlib

import bcrypt


def hash_password(password: str, rounds: int = 12) -> str:
    """Hash a password for storing.
    :param password: password to hash
    :param rounds: number of bcrypt rounds (default: 12)
    :return: hashed password"""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a stored password against one provided by the user.
    :param password: raw password to check
    :param hashed: hashed password from the database
    :return: boolean indicating whether the passwords matched"""

    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def hash_token(token: str) -> str:
    """Hash a token for secure storage.
    :param token: token to hash
    :return: hashed token"""

    return hashlib.sha256(token.encode()).hexdigest()
