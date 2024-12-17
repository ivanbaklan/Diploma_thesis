import asyncio
import math
import os
import re

import ffmpeg
from yt_dlp import YoutubeDL

from contextly.models.video import Video
# from contextly.utils.summarizer import Summarizer
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

    async def process_chunk(self, start_time: int, video_path: str, output_path: str):
        """
        Обработка отдельного куска аудио.
        """
        await asyncio.to_thread(
            lambda: ffmpeg.input(video_path, ss=start_time, t=self.chunk_duration)
            .output(output_path, format="mp3", **{"q:a": 0})
            .run(overwrite_output=True)
        )
        print(f"Saved: {output_path}")

    async def split_audio(self, video_path: str, output_path: str) -> list:
        """
        Извлечение аудио и сохранение частями.

        :param video_path: Путь к видеофайлу.
        :param output_template: Шаблон имени выходных файлов, например, "output_chunk_%03d.mp3".
        :param chunk_duration: Длительность каждого аудиофайла в секундах (по умолчанию 600 секунд = 10 минут).
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

    def dl_progress_hook(self, data: dict):
        dl_progress = 0
        if data["status"] == "downloading" and data["total_bytes"] > 0:
            dl_progress = int(data["downloaded_bytes"] / data["total_bytes"] * 100)
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
    async def async_dl_progress_hook(info):
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

    async def download_video_with_async_hook(self, video: Video):
        options = {
            "quiet": True,
            "format": "best",
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
        with YoutubeDL(thumbnail_options) as ydl:
            await loop.run_in_executor(None, ydl.download, [video.url])
        with YoutubeDL(options) as ydl:
            await loop.run_in_executor(None, ydl.download, [video.url])
        video = await Video.filter(id=video.id).first()
        audios = await self.split_audio(
            f"downloads/{video.id}/video/{video.id}.mp4",
            f"downloads/{video.id}/audio/",
        )
        video.audio_chunks = len(audios)
        video.status = "transcribe"
        await video.save()
        t = Transcriber()
        text = await t.transcribe(audios)
        video.text = text
        await video.save()
        video.status = "summarize"
        await video.save()
        # s = Summarizer()
        # description = await s.get_summary(text)
        # video.description = description
        video.status = "done"
        await video.save()
