from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
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
    """Returning-user menu: just open the marketplace (role chosen once at onboarding)."""
    return open_marketplace_kb(lang)


def role_choice_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """First-run role choice: register as a regular buyer, or as a master (usta).

    Buyer is a callback (the bot then asks for a phone via contact-share);
    master is a WebApp button that opens the Mini App registration form.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_role_buyer", lang), callback_data="role:buyer")
    )
    master_url = _miniapp_url("master")
    if _can_webapp():
        master_btn = InlineKeyboardButton(
            text=t("btn_become_master", lang), web_app=WebAppInfo(url=master_url)
        )
    else:
        # Dev fallback (non-HTTPS): plain link instead of a WebApp button.
        master_btn = InlineKeyboardButton(text=t("btn_become_master", lang), url=master_url)
    builder.row(master_btn)
    return builder.as_markup()


def share_phone_kb(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Reply keyboard with a single 'share my phone number' contact button."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_share_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


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
