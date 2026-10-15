from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import chats_keyboard, limits_keyboard
from bot.states import SummaryFlow
from user_client import UserClient, list_dialogs

logger = logging.getLogger(__name__)
router = Router(name="chats")


@router.message(Command("chats"))
async def cmd_chats(message: Message, user_client: UserClient) -> None:
    """Show recent dialogs as inline buttons; picking one asks for the limit."""
    try:
        chats = await list_dialogs(user_client, limit=40)
    except Exception:
        logger.exception("Failed to list dialogs")
        await message.answer("❌ Не удалось получить список диалогов (см. логи).")
        return

    if not chats:
        await message.answer("Диалогов не найдено.")
        return

    await message.answer(
        "💬 <b>Последние чаты</b> — выбери, по которому сделать самари:",
        reply_markup=chats_keyboard(chats, page=0),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("page:"))
async def cb_page(callback: CallbackQuery, user_client: UserClient) -> None:
    page = int(callback.data.split(":")[1])
    try:
        chats = await list_dialogs(user_client, limit=40)
        await callback.message.edit_reply_markup(reply_markup=chats_keyboard(chats, page=page))
        await callback.answer()
    except Exception:
        logger.exception("Failed to page dialogs")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("sum:"))
async def cb_pick_chat(callback: CallbackQuery, state: FSMContext) -> None:
    """Chat picked -> remember it and ask how many messages to summarize."""
    chat_id = int(callback.data.split(":")[1])
    await state.set_state(SummaryFlow.waiting_limit)
    await state.update_data(selected_chat=str(chat_id))
    await callback.message.edit_text(
        "Сколько последних сообщений просуммировать?",
        reply_markup=limits_keyboard(),
    )
    await callback.answer()
