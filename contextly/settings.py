import sys

from fastapi.templating import Jinja2Templates
from loguru import logger
from passlib.context import CryptContext

SECRET_KEY = "your_secret_key"  # secret key for use in cookie
ALGORITHM = "HS256"  # crypto algoritm for cookie
ACCESS_TOKEN_EXPIRE_MINUTES = 360  # access token expire time for cookie


templates = Jinja2Templates(directory="contextly/templates")  # template folder
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)  # crypto config for password


# config Loguru
logger.remove()  # remove standard logger
logger.add(  # add loguru logger
    sys.stderr,
    level="INFO",
    format="{time} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
