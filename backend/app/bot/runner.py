from __future__ import annotations

import asyncio
import logging

from app.bot.instance import close_bot, get_bot, get_dispatcher
from app.core.config import settings

logger = logging.getLogger(__name__)

_polling_task: asyncio.Task | None = None


def webhook_path() -> str:
    return f"/telegram/webhook/{settings.webhook_secret}"


async def start_bot() -> None:
    """Start the bot in polling (dev) or webhook (prod) mode. No-op without a token."""
    global _polling_task
    bot = get_bot()
    if bot is None:
        logger.warning("BOT_TOKEN not set — Telegram bot disabled (API still runs).")
        return

    dp = get_dispatcher()
    if settings.bot_mode == "webhook":
        url = settings.public_base_url.rstrip("/") + webhook_path()
        await bot.set_webhook(url, drop_pending_updates=True)
        logger.info("Telegram webhook set to %s", url)
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        _polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        logger.info("Telegram bot polling started.")


async def stop_bot() -> None:
    global _polling_task
    if _polling_task is not None:
        _polling_task.cancel()
        try:
            await _polling_task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass
        _polling_task = None
    await close_bot()
