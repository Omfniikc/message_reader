from __future__ import annotations

import logging
from dataclasses import dataclass

from config import Settings
from summarizer import Summarizer
from user_client import UserClient, fetch_messages, format_transcript, resolve_chat
from user_client.chats import ChatInfo

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    chat: ChatInfo
    messages_used: int
    summary: str


async def summarize_chat(
    user_client: UserClient,
    summarizer: Summarizer,
    settings: Settings,
    chat_query: str,
    limit: int | None = None,
    instructions: str | None = None,
    on_stage=None,
) -> SummaryResult:
    """Resolve chat -> fetch latest messages -> build transcript -> summarize.

    `on_stage(name, count)` is an optional async callback invoked before each
    phase ("reading" / "summarizing") so the UI can show progress.
    """
    limit = limit or settings.default_message_limit
    limit = max(1, min(limit, settings.max_message_limit))

    info = await resolve_chat(user_client, chat_query)
    logger.info("Summarizing chat %s (%s), limit=%d", info.title, info.id, limit)

    if on_stage:
        await on_stage("reading", 0)
    messages = await fetch_messages(user_client, info.id, limit)
    if not messages:
        raise ValueError(f"В чате «{info.title}» нет текстовых сообщений за последние {limit} шт.")

    if on_stage:
        await on_stage("summarizing", len(messages))
    transcript = format_transcript(messages, info.title, settings.max_transcript_chars)
    summary = await summarizer.summarize(transcript, instructions)
    if not summary:
        raise RuntimeError("LLM вернула пустой ответ")

    return SummaryResult(chat=info, messages_used=len(messages), summary=summary)
