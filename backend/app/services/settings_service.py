from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.models.setting import KEY_DEFAULT_COMMISSION, KEY_DEFAULT_DELIVERY_COST, Setting


async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    row = await session.get(Setting, key)
    return row.value if row else default


async def set_setting(session: AsyncSession, key: str, value: str) -> Setting:
    row = await session.get(Setting, key)
    if row is None:
        row = Setting(key=key, value=value)
        session.add(row)
    else:
        row.value = value
    await session.flush()
    return row


async def get_default_commission(session: AsyncSession) -> Decimal:
    raw = await get_setting(session, KEY_DEFAULT_COMMISSION)
    if raw:
        try:
            return Decimal(raw)
        except (ValueError, ArithmeticError):
            pass
    return Decimal(str(app_settings.default_commission_percent))


async def get_default_delivery_cost(session: AsyncSession) -> Decimal:
    raw = await get_setting(session, KEY_DEFAULT_DELIVERY_COST)
    if raw:
        try:
            return Decimal(raw)
        except (ValueError, ArithmeticError):
            pass
    return Decimal(str(app_settings.default_delivery_cost))


async def all_settings(session: AsyncSession) -> dict[str, str]:
    result = await session.execute(select(Setting))
    return {s.key: s.value for s in result.scalars().all()}
