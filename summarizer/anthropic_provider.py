from __future__ import annotations

import logging

from anthropic import AsyncAnthropic

from summarizer.base import Summarizer
from summarizer.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class AnthropicSummarizer(Summarizer):
    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self.model = model
        self._client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    async def summarize(self, transcript: str, instructions: str | None = None) -> str:
        resp = await self._client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.3,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": build_user_prompt(transcript, instructions)},
            ],
        )
        # Concatenate text blocks from the response.
        parts = [block.text for block in resp.content if getattr(block, "type", None) == "text"]
        return "\n".join(parts).strip()
