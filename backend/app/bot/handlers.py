from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from app.bot.keyboards import language_kb, start_kb
from app.core.config import settings
from app.db.session import SessionLocal
from app.i18n import t
from app.models.enums import Language
from app.models.user import User

router = Router()


async def _get_or_create_user(tg) -> User:
    async with SessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == tg.id))
        ).scalar_one_or_none()
        if user is None:
            lang = (
                Language.uz if (tg.language_code == "uz") else Language(settings.default_language)
            )
            user = User(
                telegram_id=tg.id,
                username=tg.username or "",
                first_name=tg.first_name or "",
                last_name=tg.last_name or "",
                language=lang,
                is_admin=tg.id in settings.admin_ids,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


async def _set_language(tg_id: int, lang: str) -> None:
    async with SessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == tg_id))
        ).scalar_one_or_none()
        if user is not None:
            user.language = Language(lang)
            await session.commit()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = await _get_or_create_user(message.from_user)
    lang = user.language.value
    kb = start_kb(lang)
    text = t("start_welcome", lang)
    if kb is None:
        # WebApp buttons require HTTPS; fall back to a plain link/hint.
        text += f"\n\n{settings.miniapp_url}"
    await message.answer(text, reply_markup=kb)
    await message.answer(t("choose_language", lang), reply_markup=language_kb())


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    user = await _get_or_create_user(message.from_user)
    await message.answer(t("choose_language", user.language.value), reply_markup=language_kb())


@router.callback_query(F.data.startswith("setlang:"))
async def cb_setlang(callback: CallbackQuery) -> None:
    lang = callback.data.split(":", 1)[1]
    if lang not in ("ru", "uz"):
        await callback.answer()
        return
    await _set_language(callback.from_user.id, lang)
    await callback.answer(t("language_set", lang))
    kb = start_kb(lang)
    text = t("start_welcome", lang)
    if kb is None:
        text += f"\n\n{settings.miniapp_url}"
    if callback.message is not None:
        await callback.message.answer(text, reply_markup=kb)
