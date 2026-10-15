from __future__ import annotations

import logging
from dataclasses import dataclass

from telethon.tl.types import Channel, Chat, User

from user_client.client import UserClient

logger = logging.getLogger(__name__)


@dataclass
class ChatInfo:
    id: int
    title: str
    username: str | None
    kind: str  # "private" | "group" | "channel"

    def label(self) -> str:
        if self.username:
            return f"@{self.username}"
        return self.title


def _kind_of(entity: object) -> str:
    if isinstance(entity, Channel):
        return "channel" if entity.broadcast else "group"
    if isinstance(entity, Chat):
        return "group"
    if isinstance(entity, User):
        return "private"
    return "unknown"


async def list_dialogs(uc: UserClient, limit: int = 30) -> list[ChatInfo]:
    """Return the most recently active dialogs of the account."""
    dialogs = await uc.client.get_dialogs(limit=limit)
    result: list[ChatInfo] = []
    for d in dialogs:
        if d.entity is None:
            continue
        result.append(
            ChatInfo(
                id=d.id,
                title=d.title or d.name or str(d.id),
                username=getattr(d.entity, "username", None),
                kind=_kind_of(d.entity),
            )
        )
    return result


async def resolve_chat(uc: UserClient, query: str) -> ChatInfo:
    """Resolve a chat by @username, numeric id, or a case-insensitive title substring.

    Raises ValueError when nothing matches or the match is ambiguous.
    """
    query = query.strip()
    if not query:
        raise ValueError("Пустой запрос чата")

    # 1) @username or t.me link
    if query.startswith("@") or "t.me/" in query:
        name = query
        if "t.me/" in name:
            name = name.split("t.me/")[-1].split("/")[0]
        name = name.lstrip("@")
        entity = await uc.client.get_entity(name)
        return ChatInfo(
            id=entity.id,
            title=getattr(entity, "title", None) or _user_full_name(entity) or name,
            username=getattr(entity, "username", None),
            kind=_kind_of(entity),
        )

    # 2) numeric id (possibly with -100 prefix for channels/supergroups)
    if query.lstrip("-").isdigit():
        entity = await uc.client.get_entity(int(query))
        return ChatInfo(
            id=entity.id,
            title=getattr(entity, "title", None) or _user_full_name(entity) or query,
            username=getattr(entity, "username", None),
            kind=_kind_of(entity),
        )

    # 3) fuzzy title match among dialogs
    needle = query.lower()
    dialogs = await uc.client.get_dialogs(limit=200)
    matches = [d for d in dialogs if needle in (d.title or "").lower()]
    if not matches:
        raise ValueError(f"Чат «{query}» не найден среди диалогов")
    if len(matches) > 1:
        names = ", ".join((m.title or "?") for m in matches[:5])
        raise ValueError(f"Найдено несколько чатов: {names}. Уточни запрос или используй @username/id.")
    d = matches[0]
    return ChatInfo(
        id=d.id,
        title=d.title or str(d.id),
        username=getattr(d.entity, "username", None),
        kind=_kind_of(d.entity),
    )


def _user_full_name(entity: object) -> str | None:
    first = getattr(entity, "first_name", None)
    last = getattr(entity, "last_name", None)
    name = " ".join(part for part in (first, last) if part)
    return name or None
