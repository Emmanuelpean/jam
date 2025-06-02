"""
This module handles authentication and authorization functionality for the application, including the creation, verification,
and usage of JWT access tokens.

Key Features:
-------------
1. **Token Creation**:
   - Generates JSON Web Tokens (JWT) with an expiration time using a secret key and algorithm defined in the application's configuration.

2. **Token Verification**:
   - Decodes and verifies JWTs by checking their validity and extracting user information (e.g., user ID).

3. **Current User Retrieval**:
   - Extracts the current authenticated user based on the token included in requests and validates against the database.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app import models, database, schemas
from app.config import settings
from app.schemas import TokenData

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict) -> str:
    """Create a JWT access token.
    :param data: The data to be encoded into the JWT access token.
    :returns: The JWT access token."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(
    token: str,
    credentials_exception: Exception,
) -> TokenData:
    """Verify the JWT access token.
    :param token: JWT access token to be verified.
    :param credentials_exception: The exception to be raised if the token is invalid or the user ID is not found.
    :returns: object containing the user ID extracted from the token."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = str(payload.get("user_id"))

        if user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=user_id)

    except jwt.JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> models.User | None:
    """Get the current user from the token and check if the token has expired.
    :param token: The JWT access token.
    :param db: The database session.
    :returns: The current user or None"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(token.id == models.User.id).first()
    return user
