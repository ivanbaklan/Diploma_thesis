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
    """
    Class YouTubeDl download a video and its thumbnail,
    extract audio, transcribe, and summarize content.
    """

    def __init__(self, chunk_duration: int = 600):
        self.chunk_duration = chunk_duration

    @staticmethod
    async def get_video_duration(video_path: str) -> float:
        """
        This function uses ffmpeg to probe the provided video
        file and extracts its duration in seconds.

        :param video_path: (str) Path to video file.
        :return (float) duration in seconds.
        """

        probe = ffmpeg.probe(video_path)
        return float(probe["format"]["duration"])

    async def process_chunk(
        self, start_time: int, video_path: str, output_path: str
    ) -> None:
        """
        Process a single chunk of audio from a video file.
        This function extracts a specific chunk of audio from the input video file
        starting at the given time and saves it to the specified output path in MP3 format.
        The chunk duration is determined by the `self.chunk_duration` attribute.

        :param start_time: (int) The start time of the audio chunk in seconds.
        :param video_path: (str) The path to the input video file.
        :param output_path: (str) The path to save the extracted audio file.
        :return None
        """

        await asyncio.to_thread(
            lambda: ffmpeg.input(video_path, ss=start_time, t=self.chunk_duration)
            .output(output_path, format="mp3", **{"q:a": 0})
            .run(overwrite_output=True)
        )
        logger.info(f"Saved: {output_path}")

    async def split_audio(self, video_path: str, output_path: str) -> list:
        """
        Split a video's audio into chunks and save them as separate files.

        :param video_path: (str) Path to video file.
        :param output_path: (str) Path to save audio,
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
        """
        Synchronous function for handling video processing progress callback

        :param data: (dict) video processing progress
        :return: None
        """

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
        """
        Processing video processing progress and saving status

        :param info: (dict) processing data
        :return: None
        """

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
        """
        Download a video and its thumbnail, extract audio, transcribe, and summarize content.

        This function handles the entire video processing pipeline, which includes:
        - Downloading the video and its thumbnail using `YoutubeDL`.
        - Extracting audio from the downloaded video and splitting it into chunks.
        - Transcribing the audio into text.
        - Summarizing the transcribed text into a concise description.

        :param video: (Video) item of db model
        :return: None
        """

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
