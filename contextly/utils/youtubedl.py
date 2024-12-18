import asyncio
import math
import os
import re

import ffmpeg
from yt_dlp import YoutubeDL

from contextly.models.video import Video
from contextly.settings import logger
from contextly.utils.summarizer import Summarizer
from contextly.utils.transcriber import Transcriber


class YouTubeDl:
    def __init__(self, chunk_duration: int = 600):
        self.chunk_duration = chunk_duration

    @staticmethod
    async def get_video_duration(video_path: str) -> float:
        """
        Получить длительность видео в секундах.
        """
        probe = ffmpeg.probe(video_path)
        return float(probe["format"]["duration"])

    async def process_chunk(
        self, start_time: int, video_path: str, output_path: str
    ) -> None:
        """
        Processing a single chunk of audio.
        """
        await asyncio.to_thread(
            lambda: ffmpeg.input(video_path, ss=start_time, t=self.chunk_duration)
            .output(output_path, format="mp3", **{"q:a": 0})
            .run(overwrite_output=True)
        )
        logger.info(f"Saved: {output_path}")

    async def split_audio(self, video_path: str, output_path: str) -> list:
        """
        Extract audio use chunks.

        :param video_path: Path to video file.
        :param output_path: Path to save audio,
        """
        os.mkdir(output_path)
        total_duration = await self.get_video_duration(video_path)
        num_chunks = math.ceil(total_duration / self.chunk_duration)

        files = [f"{output_path}{i}.mp3" for i in range(num_chunks)]
        tasks = [
            self.process_chunk(
                start_time=i * self.chunk_duration,
                output_path=f"{output_path}{i}.mp3",
                video_path=video_path,
            )
            for i in range(num_chunks)
        ]
        await asyncio.gather(*tasks)
        return files

    def dl_progress_hook(self, data: dict) -> None:
        dl_progress = 0
        try:
            if data["status"] == "downloading" and data["total_bytes"] > 0:
                dl_progress = int(data["downloaded_bytes"] / data["total_bytes"] * 100)
        except Exception as e:
            logger.error(f"Error percent count: {e}")
        info = {
            "status": data["status"],
            "filename": data["filename"],
            "title": data["info_dict"]["title"],
            "dl_progress": dl_progress,
        }
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_dl_progress_hook(info))

    @staticmethod
    async def async_dl_progress_hook(info: dict) -> None:
        uuid_pattern = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        id = re.findall(uuid_pattern, info["filename"])[0]
        video = await Video.filter(id=id).first()
        if info.get("title"):
            video.title = info["title"]
        if info["status"] == "downloading":
            video.status = f"""{info["status"]}-{info["dl_progress"]}%"""
        else:
            video.status = f"""{info["status"]}"""
        await video.save()

    async def download_video_with_async_hook(self, video: Video) -> None:
        options = {
            "quiet": True,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "outtmpl": f"downloads/{video.id}/video/{video.id}.%(ext)s",
            "progress_hooks": [self.dl_progress_hook],
        }
        thumbnail_options = {
            "quiet": True,
            "writethumbnail": True,
            "skip_download": True,
            "outtmpl": f"downloads/{video.id}/img/{video.id}.%(ext)s",
        }
        loop = asyncio.get_event_loop()

        logger.info(f"Download thumbnail start: {video.id} {video.url}")
        with YoutubeDL(thumbnail_options) as ydl:
            try:
                await loop.run_in_executor(None, ydl.download, [video.url])
            except Exception as e:
                logger.error(f"YoutubeDL error load thumbnail error: {e}")

        logger.info(f"Download video start: {video.id} {video.url}")
        with YoutubeDL(options) as ydl:
            try:
                await asyncio.shield(
                    loop.run_in_executor(None, ydl.download, [video.url])
                )
            except Exception as e:
                logger.error(f"YoutubeDL error load video error: {e}")
        video = await Video.filter(id=video.id).first()

        logger.info(f"Extract audio start: {video.id} {video.url}")
        audios = await self.split_audio(
            f"downloads/{video.id}/video/{video.id}.mp4",
            f"downloads/{video.id}/audio/",
        )
        video.audio_chunks = len(audios)
        video.status = "transcribe"
        await video.save()

        logger.info(f"Transcribe audio start: {video.id} {video.url}")
        logger.info(f"Audios: {audios}")
        transcribe = Transcriber()
        text = await transcribe.transcribe(audios)
        video.text = text
        await video.save()

        logger.info(f"Summarize text start: {video.id} {video.url}")
        video.status = "summarize"
        await video.save()
        try:
            summary = Summarizer()
            await summary.load_model()
            description = await summary.get_summary(text)
            video.description = description
        except Exception as e:
            logger.error(f"Summarizer error: {e}")
        video.status = "done"
        await video.save()
        logger.info(f"Done: {video.id} {video.url}")
