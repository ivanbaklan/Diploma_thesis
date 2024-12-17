import asyncio
from textwrap import wrap

from transformers import AutoTokenizer, T5ForConditionalGeneration


class Summarizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("contextly/utils/saved_model")
        self.model = T5ForConditionalGeneration.from_pretrained(
            "contextly/utils/saved_model"
        )
        self.max_chunk_length = 700

    async def get_summary(self, text):
        return await asyncio.to_thread(self._get_summary, text)

    def _get_summary(self, text):
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
                input_ids=input_ids, max_length=55, no_repeat_ngram_size=6
            )
            summary = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            result.append(summary)
        return " ".join(result)
