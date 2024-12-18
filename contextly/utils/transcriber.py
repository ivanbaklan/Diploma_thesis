import asyncio
import os
from typing import List

import whisper


class Transcriber:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def transcribe(self, audios_path: List[os.PathLike]):
        # text = await asyncio.to_thread(self._transcribe, audios_path)
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._transcribe, audios_path)
        return text

    def _transcribe(self, audios_path: List[os.PathLike]):
        """Function to transcribe audio using Whisper"""
        result = ""
        for file_path in audios_path:
            audio = whisper.load_audio(f"{os.getcwd()}/{file_path}")
            chunk = self.model.transcribe(audio)
            result += chunk["text"]
        return result
