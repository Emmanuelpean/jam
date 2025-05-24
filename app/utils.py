import bcrypt


def hash_password(password: str) -> str:
    """Hash a password for storing.
    :param password: password to hash"""

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a stored password against one provided by user.
    :param password: password to check against
    :param hashed: hashed password from database
    :return: boolean indicating whether password matched"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
