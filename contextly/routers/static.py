import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/static", tags=["static"])


@router.get("/thumbnail/{id}", include_in_schema=False)
async def thumbnail(id: str):
    try:
        thumbnail_path = Path(f"downloads/{uuid.UUID(id)}/img/{id}.webp")
        if thumbnail_path.exists():
            return FileResponse(thumbnail_path)
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Thumbnail not found")


@router.get("/video/{id}", include_in_schema=False)
async def video(id: str):
    try:
        video_path = Path(f"downloads/{uuid.UUID(id)}/video/{id}.mp4")
        if video_path.exists():
            return FileResponse(video_path)
        raise HTTPException(status_code=404, detail="Video not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Video not found")


@router.get("/audio/{id}", include_in_schema=False)
async def audio(id: str):
    try:
        audio_path = Path(f"downloads/{uuid.UUID(id)}/audio/0.mp3")
        if audio_path.exists():
            return FileResponse(audio_path)
        raise HTTPException(status_code=404, detail="Audio not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Audio not found")
