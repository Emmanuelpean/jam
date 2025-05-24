from jose import jwt
from datetime import datetime, timedelta, timezone
from app import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    """Create a JWT access token.
    :param data: The data to be encoded into the JWT access token.
    :type data: dict
    :returns: The JWT access token.
    :rtype: str"""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    """Verify the JWT access token.
    :param token: The JWT access token to be verified.
    :type token: str
    :param credentials_exception: The exception to be raised if the token is invalid or the user ID is not found.
    :type credentials_exception: Exception
    :returns: An object containing the user ID extracted from the token.
    :rtype: TokenData
    :raises credentials_exception: If the token is invalid or the user ID is not found.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("user_id"))

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
    except jwt.JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    """Get the current user from the token and check if the token has expired.
    :param token: The JWT access token.
    :type token: str
    :returns: The current user.
    :rtype: schemas.User"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
