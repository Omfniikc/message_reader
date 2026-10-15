from __future__ import annotations

import logging

from openai import AsyncOpenAI

from summarizer.base import Summarizer
from summarizer.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class OpenAISummarizer(Summarizer):
    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def summarize(self, transcript: str, instructions: str | None = None) -> str:
        resp = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(transcript, instructions)},
            ],
            temperature=0.3,
        )
        return (resp.choices[0].message.content or "").strip()
