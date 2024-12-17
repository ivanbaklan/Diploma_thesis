import asyncio
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from contextly.models.user import UserSchema
from contextly.models.video import Video
from contextly.settings import logger, templates
from contextly.utils.auth import auth_cookies
from contextly.utils.youtubedl import YouTubeDl

router = APIRouter(prefix="/video", tags=["video"])


@router.get("/download", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, user: Optional[UserSchema] = None):
    context = {"title": "Download"}
    return templates.TemplateResponse(request, "download.html", context=context)


@router.post("/download", response_class=HTMLResponse)
@auth_cookies
async def download_page(
    request: Request, url: Annotated[str, Form()], user: Optional[UserSchema] = None
):
    context = {"title": "Download"}
    existing_video = await Video.filter(url=url).first()
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
    videos = await Video.filter(user_id=user.id)
    context = {"videos": videos, "title": "Videos"}
    return templates.TemplateResponse(request, "download_list.html", context=context)


@router.get("/download_list/{id}", response_class=HTMLResponse)
@auth_cookies
async def download_page(request: Request, id: str, user: Optional[UserSchema] = None):
    video = await Video.filter(id=uuid.UUID(id), user_id=user.id).first()
    context = {"video": video, "title": f"Videos {video.title}"}
    return templates.TemplateResponse(request, "video.html", context=context)
