from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from tortoise.contrib.fastapi import RegisterTortoise

from contextly.db import TORTOISE_ORM
from contextly.routers.static import router as static_router
from contextly.routers.user import router as user_router
from contextly.routers.video import router as video_router
from contextly.settings import templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(static_router)
app.include_router(user_router)
app.include_router(video_router)


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """
    Renders the main page of the application.

    :param request: (Request): The HTTP request object.
    :return: HTMLResponse: The rendered main page (`index.html`) template with the context.
    """

    context = {"title": "Main"}
    return templates.TemplateResponse(request, "index.html", context=context)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Returns the favicon of the application.

    :return:  FileResponse: The favicon.ico file.
    """

    return FileResponse("contextly/favicon.ico")
