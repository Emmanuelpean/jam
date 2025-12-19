"""This module handles authentication and authorisation functionality for the application, including the creation,
verification, and usage of JWT access tokens."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app import models, database, schemas
from app.config import settings
from app.utils import AppLogger


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

logger = AppLogger.create_service_logger("oauth2")

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

    # Log token prefix for tracking (never log full token)
    token_prefix = token[:10] if token else "None"
    logger.info(f"Verifying token starting with: {token_prefix}...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token decoded successfully. Payload keys: {list(payload.keys())}")

        # Log expiration details
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            time_until_expiry = exp_datetime - datetime.now()
            logger.info(f"Token expiration: {exp_datetime}, Time remaining: {time_until_expiry}")
        else:
            logger.warning("Token has no expiration claim")

        user_id = payload.get("user_id")
        logger.info(f"Extracted user_id: {user_id}")

        if user_id is None:
            logger.error("user_id is None in token payload")
            raise credentials_exception

        token_version: int = payload.get("token_version", 0)
        logger.info(f"Token version from payload: {token_version}")

        token_data = schemas.TokenData(id=str(user_id), token_version=token_version)
        logger.info(f"Token verification successful for user {user_id}")

    except jwt.exceptions.ExpiredSignatureError:
        logger.error(f"Token expired. Token prefix: {token_prefix}")
        raise credentials_exception
    except jwt.exceptions.InvalidTokenError as e:
        logger.error(f"Invalid token error: {type(e).__name__} - {str(e)}")
        raise credentials_exception
    except jwt.exceptions.PyJWTError as e:
        logger.error(f"JWT decode error: {type(e).__name__} - {str(e)}")
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

    logger.info("get_current_user called")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    logger.info(f"Looking up user with id: {token_data.id}")

    user = db.query(models.User).filter(token_data.id == models.User.id).first()

    if user is None:
        logger.error(f"User not found in database for id: {token_data.id}")
        raise credentials_exception

    logger.info(f"User found: id={user.id}, db token_version={user.token_version}")

    # Verify token version matches current user's token version
    if user.token_version != token_data.token_version:
        logger.warning(
            f"Token version mismatch for user {user.id}. "
            f"Token version: {token_data.token_version}, "
            f"DB version: {user.token_version}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Token validation complete for user {user.id}")
    return user
