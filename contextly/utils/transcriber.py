import asyncio

import whisper


class Transcriber:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def transcribe(self, audios_path: list):
        text = await asyncio.to_thread(self._transcribe, audios_path)
        return text

    def _transcribe(self, audios_path: list):
        """Function to transcribe audio using Whisper"""
        result = ""
        for file_path in audios_path:
            audio = whisper.load_audio(file_path)
            chunk = self.model.transcribe(audio)
            result += chunk["text"]
        return result
