import functools
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from contextly.models.user import User
from contextly.settings import ALGORITHM, SECRET_KEY, pwd_context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain-text password matches the hashed password.

    :param plain_password: (str) plain-text password
    :param hashed_password: (str) hashed password
    :return: (bool)
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using a secure hashing algorithm.

    :param password: (str) plain-text password
    :return: (str) hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JSON Web Token (JWT) for user authentication.

    :param data: (dict) The payload to encode in the token (e.g., user data).
    :param expires_delta: (timedelta | None): The duration before the token expires.
        Defaults to 15 minutes if not specified.
    :return: (str) The encoded JWT.
    """

    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def auth_cookies(func: callable) -> callable:
    """
    Decorator to authenticate users using session cookies.

    Ensures the user has a valid session token before accessing the decorated route.
    Redirects unauthenticated users to the login page.

    :param func: (callable): The function to wrap with authentication.
    :return: callable: The wrapped function.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            return RedirectResponse(url="/user/login")
        token = request.cookies.get("session")
        if not token:
            return RedirectResponse(url="/user/login")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            user = await User.filter(email=email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        except JWTError:
            return RedirectResponse(url="/user/login")
        kwargs["user"] = user
        result = await func(*args, **kwargs)
        return result

    return wrapper
