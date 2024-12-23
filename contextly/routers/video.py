import asyncio
import shutil
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from contextly.models.user import UserSchema
from contextly.models.video import Video
from contextly.settings import logger, templates
from contextly.utils.auth import auth_cookies
from contextly.utils.youtubedl import YouTubeDl

router = APIRouter(prefix="/video", tags=["video"])


@router.get("/download", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, user: Optional[UserSchema] = None):
    """
    Renders the download page where the user can input a URL to download a video.

    :param request: (Request): The HTTP request object.
    :param user: (Optional[UserSchema]): The authenticated user (from the cookie).
    :return: HTMLResponse: The rendered download page template.
    """
    context = {"title": "Download"}
    return templates.TemplateResponse(request, "download.html", context=context)


@router.post("/download", response_class=HTMLResponse)
@auth_cookies
async def download_page(
    request: Request, url: Annotated[str, Form()], user: Optional[UserSchema] = None
):
    """
    Handles the submission of a video URL to be downloaded. If the video has already been downloaded,
    provides a link to the existing video. Otherwise, initiates the download process.

    :param request: (Request): The HTTP request object.
    :param url: (str): The URL of the video to be downloaded.
    :param user: (Optional[UserSchema]): The authenticated user (from the cookie).
    :return: HTMLResponse: The rendered download page template with a success or error message.
    """

    context = {"title": "Download"}
    existing_video = await Video.filter(url=url, user_id=user.id).first()
    if existing_video:
        context["info"] = f"Video Already exist, {existing_video.title}"
        context["info_url"] = f"/video/download_list/{existing_video.id}"
        logger.info("Already exist")
        return templates.TemplateResponse(request, "download.html", context=context)
    video = await Video.create(url=url, user_id=user.id)
    ytdl = YouTubeDl()
    asyncio.create_task(ytdl.download_video_with_async_hook(video))
    logger.info(f"Loading {video.url}")
    context["info"] = f"Loading {video.url}"
    return templates.TemplateResponse(request, "download.html", context=context)


@router.get("/download_list", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, user: Optional[UserSchema] = None):
    """
    Renders a list of videos that the user has downloaded.

    :param request: (Request): The HTTP request object.
    :param user: (Optional[UserSchema]): The authenticated user (from the cookie).
    :return: HTMLResponse: The rendered download list page with the user's videos.
    """

    videos = await Video.filter(user_id=user.id)
    context = {"videos": videos, "title": "Videos"}
    return templates.TemplateResponse(request, "download_list.html", context=context)


@router.get("/download_list/{id}", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, id: str, user: Optional[UserSchema] = None):
    """
    Renders a specific video page based on the provided video ID.

    :param request: (Request): The HTTP request object.
    :param id: (str) The ID of the video.
    :param user: (Optional[UserSchema]): The authenticated user (from the cookie).
    :return: HTMLResponse: The rendered video page with details of the selected video.
    """

    video = await Video.filter(id=uuid.UUID(id), user_id=user.id).first()
    context = {"video": video, "title": f"Videos {video.title}"}
    return templates.TemplateResponse(request, "video.html", context=context)


@router.post("/delete/{id}", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, id: str, user: Optional[UserSchema] = None):
    """
    Deletes a video from the user's download list and removes the corresponding video files.

    :param request: (Request): The HTTP request object.
    :param id: (str): The ID of the video to be deleted.
    :param user: (Optional[UserSchema]): The authenticated user (from the cookie).
    :return: RedirectResponse: A redirect to the download list page after deletion.
    """

    video = await Video.filter(id=uuid.UUID(id), user_id=user.id).first()
    shutil.rmtree(f"downloads/{video.id}")
    await video.delete()
    return RedirectResponse(
        url="/video/download_list", status_code=status.HTTP_302_FOUND
    )
