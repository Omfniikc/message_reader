from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SummaryFlow(StatesGroup):
    """User picked a chat from /chats; waiting for the message-count choice."""

    waiting_limit = State()
