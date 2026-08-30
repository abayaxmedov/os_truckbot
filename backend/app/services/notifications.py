from __future__ import annotations

import logging

from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.bot.instance import get_bot
from app.bot.keyboards import open_order_kb
from app.core.config import settings
from app.i18n import t
from app.models.message import Message
from app.models.order import Order, SellerOrder
from app.models.user import SellerProfile, User

logger = logging.getLogger(__name__)


def status_label(status_value: str, lang: str) -> str:
    return t(f"status_{status_value}", lang)


async def _send(chat_id: int, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    bot = get_bot()
    if bot is None:
        logger.info("Bot token not configured; skipping notification to %s: %s", chat_id, text)
        return
    try:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
    except TelegramAPIError as exc:  # user hasn't started the bot, blocked, etc.
        logger.warning("Failed to notify %s: %s", chat_id, exc)


def _fmt(amount) -> str:
    return f"{int(round(float(amount))):,}".replace(",", " ")


async def notify_new_order(session: AsyncSession, order_id: int) -> None:
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.buyer),
            selectinload(Order.seller_orders).selectinload(SellerOrder.items),
            selectinload(Order.seller_orders)
            .selectinload(SellerOrder.seller)
            .selectinload(SellerProfile.user),
        )
    )
    order = result.scalar_one_or_none()
    if order is None:
        return

    buyer = order.buyer
    # Buyer confirmation
    await _send(
        buyer.telegram_id,
        t(
            "notif_order_confirmed_buyer",
            buyer.language.value,
            order_id=order.id,
            total=_fmt(order.total),
        ),
        open_order_kb(order.id, buyer.language.value),
    )

    # Seller notifications
    for so in order.seller_orders:
        seller_user = so.seller.user
        lang = seller_user.language.value
        await _send(
            seller_user.telegram_id,
            t(
                "notif_new_order_seller",
                lang,
                order_id=order.id,
                buyer=buyer.full_name or buyer.username or str(buyer.telegram_id),
                items=len(so.items),
                payout=_fmt(so.seller_payout),
                commission=_fmt(so.commission_amount),
            ),
            open_order_kb(order.id, lang),
        )

    # Admin notifications
    for admin_id in settings.admin_ids:
        await _send(
            admin_id,
            t(
                "notif_new_order_admin",
                settings.default_language,
                order_id=order.id,
                total=_fmt(order.total),
            ),
        )


async def notify_status_change(session: AsyncSession, seller_order_id: int) -> None:
    result = await session.execute(
        select(SellerOrder)
        .where(SellerOrder.id == seller_order_id)
        .options(
            selectinload(SellerOrder.order).selectinload(Order.buyer),
            selectinload(SellerOrder.seller),
        )
    )
    so = result.scalar_one_or_none()
    if so is None:
        return
    buyer = so.order.buyer
    lang = buyer.language.value
    await _send(
        buyer.telegram_id,
        t(
            "notif_status_changed_buyer",
            lang,
            order_id=so.order_id,
            status=status_label(so.status.value, lang),
            seller=so.seller.shop_name,
        ),
        open_order_kb(so.order_id, lang),
    )


async def notify_new_seller(session: AsyncSession, seller_profile_id: int) -> None:
    result = await session.execute(
        select(SellerProfile)
        .where(SellerProfile.id == seller_profile_id)
        .options(selectinload(SellerProfile.user))
    )
    sp = result.scalar_one_or_none()
    if sp is None:
        return
    for admin_id in settings.admin_ids:
        await _send(
            admin_id,
            t(
                "notif_new_seller_admin",
                settings.default_language,
                shop=sp.shop_name,
                name=sp.user.full_name or sp.user.username or str(sp.user.telegram_id),
            ),
        )


async def notify_new_message(session: AsyncSession, message_id: int) -> None:
    result = await session.execute(
        select(Message)
        .where(Message.id == message_id)
        .options(selectinload(Message.from_user), selectinload(Message.to_user))
    )
    msg = result.scalar_one_or_none()
    if msg is None:
        return
    recipient: User = msg.to_user
    lang = recipient.language.value
    sender_name = (
        msg.from_user.full_name or msg.from_user.username or str(msg.from_user.telegram_id)
    )
    await _send(
        recipient.telegram_id,
        t("notif_new_message", lang, sender=sender_name, text=msg.text),
    )
