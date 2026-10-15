from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from user_client.chats import ChatInfo

PAGE_SIZE = 8


def chats_keyboard(chats: list[ChatInfo], page: int = 0) -> InlineKeyboardMarkup:
    """Inline keyboard listing dialogs; each button carries the chat id."""
    start = page * PAGE_SIZE
    window = chats[start : start + PAGE_SIZE]

    rows: list[list[InlineKeyboardButton]] = []
    for info in window:
        icon = {"private": "👤", "group": "👥", "channel": "📢"}.get(info.kind, "💬")
        label = f"{icon} {info.title}"[:60]
        rows.append(
            [InlineKeyboardButton(text=label, callback_data=f"sum:{info.id}:{page}")]
        )

    # pagination row
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{page - 1}"))
    if start + PAGE_SIZE < len(chats):
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page:{page + 1}"))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def limits_keyboard() -> InlineKeyboardMarkup:
    """Quick-pick how many messages to summarize once a chat is chosen."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="50", callback_data="lim:50"),
                InlineKeyboardButton(text="100", callback_data="lim:100"),
                InlineKeyboardButton(text="200", callback_data="lim:200"),
            ]
        ]
    )
