from __future__ import annotations

from abc import ABC, abstractmethod


class Summarizer(ABC):
    """Generates a summary of a chat transcript."""

    @abstractmethod
    async def summarize(self, transcript: str, instructions: str | None = None) -> str:
        """Return a summary of `transcript`, optionally guided by `instructions`."""
        raise NotImplementedError
