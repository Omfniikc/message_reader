from __future__ import annotations

import asyncio
import logging

from bot.app import create_bot, create_dispatcher
from config import get_settings
from summarizer import get_summarizer
from user_client import UserClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("main")


async def main() -> None:
    settings = get_settings()

    # 1) MTProto user client (first run asks for phone + code in the terminal).
    user_client = UserClient(settings)
    await user_client.start()

    # 2) Bot interface.
    bot = create_bot(settings)
    summarizer = get_summarizer(settings)
    dp = create_dispatcher(settings, user_client, summarizer)

    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("Bot started: @%s (owner_id=%s)", me.username, settings.owner_id)

    try:
        await dp.start_polling(bot)
    finally:
        await user_client.stop()
        await bot.session.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopped by user")
