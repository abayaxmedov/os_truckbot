from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings

_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot | None:
    """Return the shared Bot instance, or None if BOT_TOKEN is not configured."""
    global _bot
    if not settings.bot_token:
        return None
    if _bot is None:
        _bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        _dp = Dispatcher(storage=MemoryStorage())
        from app.bot.handlers import router  # local import avoids circular import

        _dp.include_router(router)
    return _dp


async def close_bot() -> None:
    global _bot
    if _bot is not None:
        await _bot.session.close()
        _bot = None
