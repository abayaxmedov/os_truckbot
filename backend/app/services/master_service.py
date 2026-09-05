from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.master import MasterProfile
from app.models.user import User


def _csv(values: list[str]) -> str:
    """Join a list of codes into a clean, de-duplicated CSV string."""
    seen: list[str] = []
    for v in values:
        v = v.strip()
        if v and v not in seen:
            seen.append(v)
    return ",".join(seen)


@dataclass
class MasterInput:
    first_name: str
    last_name: str = ""
    phone: str = ""
    photo: str = ""
    address: str = ""
    card_number: str = ""
    trucks: list[str] = field(default_factory=list)
    specializations: list[str] = field(default_factory=list)
    regions: str = ""
    work_hours: str = ""
    is_24_7: bool = False
    experience_years: int | None = None
    bio: str = ""
    price_call: float | None = None
    price_diagnostics: float | None = None
    price_repair_note: str = ""


def _apply_profile(master: MasterProfile, data: MasterInput) -> None:
    """Overwrite the service-profile fields from the submitted form (full form each time)."""
    master.trucks = _csv(data.trucks)
    master.specializations = _csv(data.specializations)
    master.regions = data.regions
    master.work_hours = data.work_hours
    master.is_24_7 = data.is_24_7
    master.experience_years = data.experience_years
    master.bio = data.bio
    master.price_call = Decimal(str(data.price_call)) if data.price_call is not None else None
    master.price_diagnostics = (
        Decimal(str(data.price_diagnostics)) if data.price_diagnostics is not None else None
    )
    master.price_repair_note = data.price_repair_note


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
        _apply_profile(master, data)
        session.add(master)
    else:
        if data.photo:
            master.photo = data.photo
        master.address = data.address or master.address
        master.card_number = data.card_number or master.card_number
        _apply_profile(master, data)
    await session.flush()
    return master
