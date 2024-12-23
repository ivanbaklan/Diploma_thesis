from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from contextly.models.user import User
from contextly.settings import ACCESS_TOKEN_EXPIRE_MINUTES, logger, templates
from contextly.utils.auth import (create_access_token, get_password_hash,
                                  verify_password)

router = APIRouter(prefix="/user", tags=["user"])


async def validate_register(username, email, password, confirm_password):
    """
    Validates the user registration data.

    :param username: (str): The desired username of the user.
    :param email: (str): The desired email of the user.
    :param password: (str): The chosen password for the user.
    :param confirm_password: (str): The password confirmation.
    :return: tuple[int, str]: A tuple with status code and error message
        if validation fails, otherwise success code.
    """

    status_code = 200
    error = ""
    if not password == confirm_password:
        status_code = 400
        error = "Password and Confirm password do not match"
    existing_user = await User.filter(username=username).first()
    if existing_user:
        status_code = 400
        error = "Username already exist"
    existing_user = await User.filter(email=email).first()
    if existing_user:
        status_code = 400
        error = "Please use another email"
    return status_code, error


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    """
    Renders the registration page.

    :param request: (Request) The HTTP request object.
    :return: HTMLResponse: The rendered registration page template.
    """
    context = {"title": "Register"}
    return templates.TemplateResponse(request, "register.html", context=context)


@router.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    email: Annotated[str, Form()],
):
    """
    Handles the registration form submission and user creation.

    :param request: (Request) The HTTP request object.
    :param username: (str) The username to register.
    :param password: (str) The password for the user.
    :param confirm_password: (str) The confirmation of the password.
    :param email: (str) The email for the user.
    :return: HTMLResponse: The registration page with errors
        or a redirect to the login page.
    """

    context = {"title": "Register"}
    status_code, error = await validate_register(
        username, email, password, confirm_password
    )
    if error:
        context["error"] = error
        return templates.TemplateResponse(
            request, "register.html", status_code=status_code, context=context
        )
    user = await User.create(
        username=username, hashed_password=get_password_hash(password), email=email
    )
    logger.info(f"User: {user.username} created")
    response = RedirectResponse(url="/user/login", status_code=status.HTTP_302_FOUND)
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """
    Renders the login page.

    :param request: (Request): The HTTP request object.
    :return: HTMLResponse: The rendered login page template.
    """

    context = {"title": "Login"}
    return templates.TemplateResponse(request, "login.html", context=context)


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """
    Handles the login form submission and user authentication.

    :param request: (Request): The HTTP request object.
    :param username: (str): The username to log in.
    :param password: (str): The password for the user.
    :return: HTMLResponse: A redirect to the video download page on successful
       login or back to login with error message.
    """

    context = {"title": "Login"}
    user = await User.filter(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        error = "Incorrect login or password"
        context["error"] = error
        return templates.TemplateResponse(request, "login.html", context=context)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response = RedirectResponse(
        url="/video/download", status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/logout")
async def logout_get(request: Request):
    """
    Logout the user by deleting the session cookie.

    :param request: (Request): The HTTP request object.
    :return: RedirectResponse: A redirect to the login page after logging out.
    """

    response = RedirectResponse(url="/user/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session")
    return response
