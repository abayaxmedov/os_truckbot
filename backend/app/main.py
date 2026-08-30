from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.bot.instance import get_bot, get_dispatcher
from app.bot.runner import start_bot, stop_bot, webhook_path
from app.core.config import settings
from app.services.media import MEDIA_ROOT
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("truckbot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await start_bot()
    except Exception:  # noqa: BLE001 - never block API startup on bot errors
        logger.exception("Failed to start Telegram bot")
    start_scheduler()
    yield
    await stop_scheduler()
    try:
        await stop_bot()
    except Exception:  # noqa: BLE001
        logger.exception("Failed to stop Telegram bot")


app = FastAPI(title="TruckBot Marketplace API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*",  # Telegram Mini Apps are served from various https origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")

app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.env, "bot": bool(settings.bot_token)}


@app.get("/")
async def root() -> dict:
    return {"name": "TruckBot Marketplace API", "docs": "/docs", "api": "/api/v1"}


# Telegram webhook endpoint (used only when BOT_MODE=webhook)
@app.post(webhook_path())
async def telegram_webhook(request: Request) -> dict:
    from aiogram.types import Update

    bot = get_bot()
    if bot is None:
        return {"ok": False, "detail": "bot_disabled"}
    dp = get_dispatcher()
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
