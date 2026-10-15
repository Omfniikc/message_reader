from __future__ import annotations

from config import Settings
from summarizer.base import Summarizer

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-20250514",
}


def get_summarizer(settings: Settings) -> Summarizer:
    """Build the summarizer chosen by LLM_PROVIDER."""
    provider = settings.llm_provider.lower()
    model = settings.llm_model or DEFAULT_MODELS.get(provider)

    if provider == "openai":
        from summarizer.openai_provider import OpenAISummarizer

        return OpenAISummarizer(
            api_key=settings.llm_api_key,
            model=model,
            base_url=settings.llm_base_url,
        )
    if provider == "anthropic":
        from summarizer.anthropic_provider import AnthropicSummarizer

        return AnthropicSummarizer(
            api_key=settings.llm_api_key,
            model=model,
            base_url=settings.llm_base_url,
        )

    raise ValueError(f"Неизвестный LLM_PROVIDER: {provider!r} (ожидался 'openai' или 'anthropic')")
