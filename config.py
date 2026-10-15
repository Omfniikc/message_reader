from __future__ import annotations

from functools import lru_cache

from environs import Env
from proxy_utils import normalize_proxy_url


class Settings:
    def __init__(self) -> None:
        env = Env()
        env.read_env()

        # Telegram user account (MTProto)
        self.api_id: int = env.int("API_ID")
        self.api_hash: str = env.str("API_HASH")
        self.session_name: str = env.str("SESSION_NAME", "message_reader")

        # Bot
        self.bot_token: str = env.str("BOT_TOKEN")
        self.owner_id: int = env.int("OWNER_ID")

        # Optional proxy used by BOTH the Telethon client and the Bot API,
        # e.g. http://login:password@host:port or socks5://host:1080
        # Schemeless "host:port" is normalized to http://host:port so aiogram
        # (which requires an explicit scheme) and Telethon both accept it.
        self.proxy: str | None = normalize_proxy_url(env.str("PROXY", None))

        # LLM
        self.llm_provider: str = env.str("LLM_PROVIDER", "openai").lower()
        self.llm_api_key: str = env.str("LLM_API_KEY")
        # empty -> factory picks a sensible default per provider
        self.llm_model: str = env.str("LLM_MODEL", "")
        # Optional custom API endpoint for aggregator/proxy services that speak
        # the OpenAI or Anthropic protocol (e.g. https://tokify.sale/v1).
        # Empty -> the SDK's official default endpoint.
        self.llm_base_url: str = env.str("LLM_BASE_URL", "") or None

        # Limits
        self.default_message_limit: int = env.int("DEFAULT_MESSAGE_LIMIT", 100)
        self.max_message_limit: int = env.int("MAX_MESSAGE_LIMIT", 500)
        self.max_transcript_chars: int = env.int("MAX_TRANSCRIPT_CHARS", 60_000)


@lru_cache
def get_settings() -> Settings:
    return Settings()
