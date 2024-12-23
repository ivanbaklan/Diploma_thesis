import asyncio
from pathlib import Path
from textwrap import wrap

from transformers import AutoTokenizer, T5ForConditionalGeneration

from contextly.settings import logger


class Summarizer:
    """
    Summarizer class for generating text summaries using a pre-trained T5 model.

    This class provides methods to load a summarization model and generate summaries
    for input text. It supports chunking long text into manageable pieces for processing.
    """

    def __init__(self):
        self.model_path = "contextly/utils/saved_model"
        self.max_chunk_length = 700

    async def load_model(self):
        """
        Wrapper for load the summarization model asynchronously.

        :return: None
        """

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        """
        Load the summarization model.

        :return: None
        """

        logger.info("Init Summarizer model")
        model_path = Path(self.model_path)
        if model_path.exists():
            logger.info("Load Summarizer saved model")
            self.tokenizer = AutoTokenizer.from_pretrained(
                "contextly/utils/saved_model"
            )
            self.model = T5ForConditionalGeneration.from_pretrained(
                "contextly/utils/saved_model"
            )
        else:
            logger.info("Download and load Summarizer model")
            self.model_name = "IlyaGusev/rut5_base_sum_gazeta"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            self.model_path = "contextly/utils/saved_model"
            self.model.save_pretrained(self.model_path)
            self.tokenizer.save_pretrained(self.model_path)

    async def get_summary(self, text: str) -> str:
        """
        Wrapper for generate a summary for the given text asynchronously.

        :param text: (str) The input text to summarize.
        :return: (str) The generated summary.
        """

        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(None, self._get_summary, text)
        return summary

    def _get_summary(self, text: str) -> str:
        """
        Generate a summary for the given text

        :param text: (str) The input text to summarize.
        :return: (str) The generated summary.
        """

        result = []
        chunks = wrap(text, self.max_chunk_length)
        for i, chunk in enumerate(chunks):
            input_ids = self.tokenizer(
                chunk,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_chunk_length,
            )["input_ids"]
            output_ids = self.model.generate(
                input_ids=input_ids, max_length=55, no_repeat_ngram_size=4
            )
            summary = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            result.append(summary)
        return " ".join(result)
