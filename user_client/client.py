from __future__ import annotations

import logging

from telethon import TelegramClient

from config import Settings
from proxy_utils import telethon_proxy

logger = logging.getLogger(__name__)


class UserClient:
    """Thin wrapper around the Telethon client bound to the user's account."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: TelegramClient | None = None

    @property
    def client(self) -> TelegramClient:
        if self._client is None:
            raise RuntimeError("UserClient is not started; call start() first")
        return self._client

    async def start(self) -> TelegramClient:
        """Create and connect the MTProto client.

        On the very first run Telethon interactively asks for the phone number
        and the login code (in the terminal, not via the bot). The resulting
        .session file makes later logins automatic.
        """
        if self._client is None:
            proxy = telethon_proxy(self.settings.proxy)
            if proxy:
                logger.info("Using proxy for MTProto connection")
            self._client = TelegramClient(
                self.settings.session_name,
                self.settings.api_id,
                self.settings.api_hash,
                proxy=proxy,
            )
        # start() connects first, then checks authorization and only runs the
        # interactive login (phone + code in the terminal) when needed.
        # NOTE: do NOT call is_user_authorized() before connecting — it issues
        # a network request and raises ConnectionError while disconnected.
        await self._client.start()
        me = await self._client.get_me()
        logger.info("UserClient connected as id=%s @%s", me.id, me.username)
        return self._client

    async def stop(self) -> None:
        if self._client is not None:
            await self._client.disconnect()
            self._client = None
