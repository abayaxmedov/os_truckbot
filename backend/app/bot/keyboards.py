from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import settings
from app.i18n import t


def _miniapp_url(path: str = "") -> str:
    base = settings.miniapp_url.rstrip("/")
    if path:
        return f"{base}/{path.lstrip('/')}"
    return base


def _can_webapp() -> bool:
    # Telegram only allows WebApp buttons over HTTPS.
    return settings.miniapp_url.lower().startswith("https://")


def open_marketplace_kb(lang: str = "ru", path: str = "") -> InlineKeyboardMarkup | None:
    if not _can_webapp():
        return None
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_open_marketplace", lang),
            web_app=WebAppInfo(url=_miniapp_url(path)),
        )
    )
    return builder.as_markup()


def start_kb(lang: str = "ru") -> InlineKeyboardMarkup | None:
    """Start menu: open the marketplace, or register as a master (usta)."""
    if not _can_webapp():
        return None
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_open_marketplace", lang),
            web_app=WebAppInfo(url=_miniapp_url()),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_become_master", lang),
            web_app=WebAppInfo(url=_miniapp_url("master")),
        )
    )
    return builder.as_markup()


def open_order_kb(order_id: int, lang: str = "ru") -> InlineKeyboardMarkup | None:
    if not _can_webapp():
        return None
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("btn_open_order", lang),
            web_app=WebAppInfo(url=_miniapp_url(f"orders/{order_id}")),
        )
    )
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_lang_ru", "ru"), callback_data="setlang:ru"),
        InlineKeyboardButton(text=t("btn_lang_uz", "uz"), callback_data="setlang:uz"),
    )
    return builder.as_markup()
