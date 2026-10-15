from __future__ import annotations

import logging
from datetime import datetime

from telethon.tl.types import Message, User

from user_client.client import UserClient

logger = logging.getLogger(__name__)


def _sender_label(msg: Message, chat_title: str) -> str:
    sender = msg.sender
    if sender is None:
        if msg.sender_id is not None and msg.sender_id == msg.chat_id:
            return chat_title  # posted as the channel itself
        return "?"
    if isinstance(sender, User):
        name = " ".join(p for p in (sender.first_name, sender.last_name) if p)
        return name or (sender.username or str(sender.id))
    # Channel / Chat sender
    return getattr(sender, "title", None) or chat_title


async def fetch_messages(uc: UserClient, chat_id: int, limit: int) -> list[Message]:
    """Fetch up to `limit` latest messages, oldest-first, skipping empty/service ones."""
    entity = await uc.client.get_entity(chat_id)
    raw: list[Message] = []
    async for msg in uc.client.iter_messages(entity, limit=limit):
        if msg is None:
            continue
        # keep text-bearing messages; drop pure service actions
        text = (msg.message or "").strip()
        if not text:
            continue
        raw.append(msg)
    raw.reverse()  # iter_messages yields newest-first -> make it chronological
    return raw


def format_transcript(
    messages: list[Message],
    chat_title: str,
    max_chars: int = 60_000,
) -> str:
    """Render messages into a readable transcript.

    If the transcript exceeds `max_chars`, the OLDEST messages are dropped and
    a note is prepended, so the most recent context is always preserved.
    """
    lines: list[str] = []
    for msg in messages:
        when = msg.date
        if isinstance(when, datetime):
            when_str = when.strftime("%Y-%m-%d %H:%M")
        else:
            when_str = str(when)
        sender = _sender_label(msg, chat_title)
        text = (msg.message or "").strip()
        lines.append(f"[{when_str}] {sender}: {text}")

    # Drop oldest lines until we fit the budget.
    note = ""
    while lines and sum(len(x) + 1 for x in lines) > max_chars:
        lines.pop(0)
        note = "(показаны только самые свежие сообщения — начало переписки обрезано)\n"

    body = "\n".join(lines)
    header = f"Чат: {chat_title}\nСообщений: {len(lines)}\n\n"
    return header + note + body
