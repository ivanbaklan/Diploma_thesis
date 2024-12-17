import functools
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from contextly.models.user import User
from contextly.settings import ALGORITHM, SECRET_KEY, pwd_context


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def auth_cookies(func):
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
