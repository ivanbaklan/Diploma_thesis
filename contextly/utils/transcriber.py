import asyncio
import os
from typing import List

import whisper


class Transcriber:
    """
    Transcriber class for transcribing audio files into text using the Whisper model.

    This class provides methods to transcribe audio files asynchronously and synchronously,
    leveraging OpenAI's Whisper model.
    """

    def __init__(self):
        self.model = whisper.load_model("base")

    async def transcribe(self, audios_path: List[os.PathLike]) -> str:
        """
        Wrapper for function to transcribe audio using Whisper

        :param audios_path: (List[os.PathLike]) path to audio file
        :return: (str)
        """
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._transcribe, audios_path)
        return text

    def _transcribe(self, audios_path: List[os.PathLike]) -> str:
        """
        Function to transcribe audio using Whisper

        :param audios_path: (List[os.PathLike]) path to audio file
        :return:
        """
        result = ""
        for file_path in audios_path:
            audio = whisper.load_audio(f"{os.getcwd()}/{file_path}")
            chunk = self.model.transcribe(audio)
            result += chunk["text"]
        return result
