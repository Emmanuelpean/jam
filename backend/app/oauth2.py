"""This module handles authentication and authorisation functionality for the application, including the creation,
verification, and usage of JWT access tokens."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models, database, schemas
from app.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, token_version: int = 0) -> str:
    """Create a JWT access token with token version.
    :param data: The data to be encoded into the JWT access token.
    :param token_version: The user's current token version for invalidation tracking.
    :returns: The JWT access token."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_version": token_version})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(
    token: str,
    credentials_exception: Exception,
) -> schemas.TokenData:
    """Verify the JWT access token validity and extract the user id and token version.
    :param token: JWT access token to be verified.
    :param credentials_exception: The exception to be raised if the token is invalid or the user ID is not found.
    :returns: object containing the user ID and token version extracted from the token."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_version: int = payload.get("token_version", 0)

        token_data = schemas.TokenData(id=str(user_id), token_version=token_version)

    except jwt.PyJWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> models.User | None:
    """Get the current user from the token and verify token version is valid.
    :param token: The JWT access token.
    :param db: The database session.
    :returns: The current user or None"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(token_data.id == models.User.id).first()

    if user is None:
        raise credentials_exception

    # Verify token version matches current user's token version
    if user.token_version != token_data.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
