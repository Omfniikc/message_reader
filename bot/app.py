from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import base, chats, summarize
from bot.middlewares.owner import OwnerMiddleware
from config import Settings
from summarizer import Summarizer
from user_client import UserClient


class _InsecureAiohttpSession(AiohttpSession):
    """When routing through an HTTP proxy, skip TLS verification (mirrors TruTask-Tg)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._proxy:
            self._connector_init["ssl"] = False


def create_bot(settings: Settings) -> Bot:
    session = _InsecureAiohttpSession(proxy=settings.proxy) if settings.proxy else None
    return Bot(
        token=settings.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(
    settings: Settings,
    user_client: UserClient,
    summarizer: Summarizer,
) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(base.router, chats.router, summarize.router)

    # Single-user guard: only the owner's updates reach the handlers.
    dp.update.outer_middleware(OwnerMiddleware(settings.owner_id))

    # Inject dependencies into every handler via workflow_data.
    dp["user_client"] = user_client
    dp["summarizer"] = summarizer
    dp["settings"] = settings
    return dp
