from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.master import MasterProfile
from app.models.user import User


@dataclass
class MasterInput:
    first_name: str
    last_name: str = ""
    phone: str = ""
    photo: str = ""
    address: str = ""
    card_number: str = ""


async def register_or_update_master(
    session: AsyncSession, user: User, data: MasterInput
) -> MasterProfile:
    # Name/phone live on the user record
    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.phone:
        user.phone = data.phone
    user.onboarded = True

    master = user.master_profile
    if master is None:
        master = MasterProfile(
            user_id=user.id,
            photo=data.photo,
            address=data.address,
            card_number=data.card_number,
            next_payout_at=datetime.now(UTC) + timedelta(days=settings.payout_period_days),
        )
        session.add(master)
    else:
        if data.photo:
            master.photo = data.photo
        master.address = data.address or master.address
        master.card_number = data.card_number or master.card_number
    await session.flush()
    return master
