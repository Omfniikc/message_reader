from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.services import summarize_chat
from bot.states import SummaryFlow
from bot.sum_args import parse_sum_args
from bot.text_utils import chunk_text
from config import Settings
from summarizer import Summarizer
from user_client import UserClient

logger = logging.getLogger(__name__)
router = Router(name="summarize")


async def run_summary(
    progress_editable,
    *,
    chat_query: str,
    limit: int | None,
    instructions: str | None,
    user_client: UserClient,
    summarizer: Summarizer,
    settings: Settings,
    answer_fn,
) -> None:
    """Shared pipeline: status updates + fetch + summarize + chunked reply.

    `progress_editable` is a Message (edit-based status) or None (send-based).
    `answer_fn(text)` delivers the final summary chunks.
    """

    async def status(text: str) -> None:
        if progress_editable is not None:
            try:
                await progress_editable.edit_text(text)
                return
            except Exception:  # message not modified / too old, fall back
                pass
        await answer_fn(text)

    async def on_stage(stage: str, count: int) -> None:
        if stage == "reading":
            await status("📖 Читаю сообщения…")
        elif stage == "summarizing":
            await status(f"✍️ Генерирую самари по {count} сообщениям…")

    try:
        result = await summarize_chat(
            user_client=user_client,
            summarizer=summarizer,
            settings=settings,
            chat_query=chat_query,
            limit=limit,
            instructions=instructions,
            on_stage=on_stage,
        )
    except ValueError as e:
        await answer_fn(f"⚠️ {e}")
        return
    except Exception:
        logger.exception("Summary failed for query=%r", chat_query)
        await answer_fn("❌ Не удалось сделать самари (см. логи сервера).")
        return

    header = f"📝 <b>Самари</b> — {result.chat.label()} ({result.messages_used} сообщ.)"
    chunks = chunk_text(result.summary)
    await answer_fn(header, parse_mode="HTML")
    for chunk in chunks:
        await answer_fn(chunk)


@router.message(Command("sum"))
async def cmd_sum(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    user_client: UserClient,
    summarizer: Summarizer,
    settings: Settings,
) -> None:
    """`/sum <chat> [N] [instruction]` — summarize the latest N messages of a chat."""
    args = parse_sum_args(command.args or "")

    if args.chat_query is None:
        # No chat given: fall back to the /chats picker.
        await message.answer(
            "Укажи чат, например:\n"
            "/sum @username 50\n"
            "/sum 123456789 200 только про дедлайны\n\n"
            "Или выбери чат кнопками: /chats"
        )
        return

    progress = await message.answer("📖 Читаю сообщения…")

    async def answer_fn(text: str, parse_mode: str | None = None) -> None:
        await message.answer(text, parse_mode=parse_mode)

    await run_summary(
        progress,
        chat_query=args.chat_query,
        limit=args.limit,
        instructions=args.instructions,
        user_client=user_client,
        summarizer=summarizer,
        settings=settings,
        answer_fn=answer_fn,
    )


@router.callback_query(F.data.startswith("lim:"))
async def cb_pick_limit(
    callback: CallbackQuery,
    state: FSMContext,
    user_client: UserClient,
    summarizer: Summarizer,
    settings: Settings,
) -> None:
    """Limit button after picking a chat from /chats."""
    limit = int(callback.data.split(":")[1])
    data = await state.get_data()
    chat_query = data.get("selected_chat")
    await state.clear()
    if not chat_query:
        await callback.answer("Сессия выбора истекла — начни заново с /chats", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(f"📖 Читаю последние {limit} сообщений…")

    async def answer_fn(text: str, parse_mode: str | None = None) -> None:
        try:
            await callback.message.answer(text, parse_mode=parse_mode)
        except Exception:
            logger.exception("Failed to answer in limit callback")

    await run_summary(
        callback.message,
        chat_query=chat_query,
        limit=limit,
        instructions=None,
        user_client=user_client,
        summarizer=summarizer,
        settings=settings,
        answer_fn=answer_fn,
    )
