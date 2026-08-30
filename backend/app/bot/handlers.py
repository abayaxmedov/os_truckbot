from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy import select

from app.bot.keyboards import language_kb, role_choice_kb, share_phone_kb, start_kb
from app.core.config import settings
from app.db.session import SessionLocal
from app.i18n import t
from app.models.enums import Language
from app.models.user import User

router = Router()


class Onboarding(StatesGroup):
    """First-run flow: language (a global callback) → role → phone (buyer only)."""

    role = State()
    phone = State()


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


async def _set_phone_onboarded(tg_id: int, phone: str) -> None:
    """Buyer path: store the shared phone and mark onboarding complete."""
    async with SessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == tg_id))
        ).scalar_one_or_none()
        if user is not None:
            if phone:
                user.phone = phone
            user.onboarded = True
            await session.commit()


def _welcome_text(lang: str) -> str:
    text = t("start_welcome", lang)
    if not settings.miniapp_url.lower().startswith("https://"):
        # WebApp buttons require HTTPS; fall back to a plain link/hint.
        text += f"\n\n{settings.miniapp_url}"
    return text


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    user = await _get_or_create_user(message.from_user)
    lang = user.language.value
    if user.onboarded:
        await state.clear()
        await message.answer(_welcome_text(lang), reply_markup=start_kb(lang))
        return
    # First run: ask for language first — nothing else yet.
    await state.clear()
    await message.answer(t("choose_language", lang), reply_markup=language_kb())


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    user = await _get_or_create_user(message.from_user)
    await message.answer(t("choose_language", user.language.value), reply_markup=language_kb())


@router.callback_query(F.data.startswith("setlang:"))
async def cb_setlang(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split(":", 1)[1]
    if lang not in ("ru", "uz"):
        await callback.answer()
        return
    await _set_language(callback.from_user.id, lang)
    await callback.answer(t("language_set", lang))
    user = await _get_or_create_user(callback.from_user)
    if callback.message is None:
        return
    if user.onboarded:
        # Language changed later via the /language menu — just re-show the marketplace.
        await callback.message.answer(_welcome_text(lang), reply_markup=start_kb(lang))
        return
    # Onboarding: proceed to the role choice.
    await state.set_state(Onboarding.role)
    await callback.message.answer(t("choose_role", lang), reply_markup=role_choice_kb(lang))


@router.callback_query(F.data == "role:buyer")
async def cb_role_buyer(callback: CallbackQuery, state: FSMContext) -> None:
    user = await _get_or_create_user(callback.from_user)
    lang = user.language.value
    await callback.answer()
    if callback.message is None:
        return
    await state.set_state(Onboarding.phone)
    await callback.message.answer(t("ask_phone", lang), reply_markup=share_phone_kb(lang))


@router.message(Onboarding.phone, F.contact)
async def on_contact(message: Message, state: FSMContext) -> None:
    user = await _get_or_create_user(message.from_user)
    lang = user.language.value
    await _set_phone_onboarded(message.from_user.id, message.contact.phone_number)
    await state.clear()
    await message.answer(t("onboarded_buyer", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(_welcome_text(lang), reply_markup=start_kb(lang))


@router.message(Onboarding.phone)
async def on_phone_fallback(message: Message) -> None:
    # In the phone step but the user sent something other than a shared contact — re-ask.
    user = await _get_or_create_user(message.from_user)
    lang = user.language.value
    await message.answer(t("ask_phone", lang), reply_markup=share_phone_kb(lang))
