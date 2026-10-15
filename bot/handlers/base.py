from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="base")

HELP_TEXT = (
    "🤖 <b>message_reader</b> — самари твоих Telegram-чатов.\n\n"
    "<b>Команды:</b>\n"
    "/chats — список диалогов, самари кнопками\n"
    "/sum <i>чат</i> [N] [инструкция] — самари последних N сообщений\n\n"
    "<b>Примеры /sum:</b>\n"
    "• <code>/sum @durov 50</code>\n"
    "• <code>/sum 123456789 200 только про дедлайны</code>\n"
    "• <code>/sum рабочая группа</code> — поиск по названию\n\n"
    "Чат можно задать @username, числовым id или подстрокой названия. "
    "N по умолчанию — 100, максимум — 500."
)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Я делаю самари твоих чатов — личек, групп и каналов.\n\n" + HELP_TEXT,
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")
