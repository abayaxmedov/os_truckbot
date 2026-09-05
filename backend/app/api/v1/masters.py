from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import SessionDep
from app.models.enums import MasterStatus
from app.models.master import MasterProfile
from app.schemas.master import MasterPublicOut
from app.services.media import media_url

router = APIRouter(prefix="/masters", tags=["masters"])


def _split(csv: str) -> list[str]:
    return [c for c in (csv or "").split(",") if c]


def serialize_public(mp: MasterProfile) -> MasterPublicOut:
    user = mp.user
    name = " ".join(filter(None, [user.first_name if user else "", (user.last_name or "") if user else ""])).strip()
    return MasterPublicOut(
        id=mp.id,
        name=name,
        photo=media_url(mp.photo),
        phone=(user.phone or "") if user else "",
        is_verified=mp.is_verified,
        trucks=_split(mp.trucks),
        specializations=_split(mp.specializations),
        regions=mp.regions,
        work_hours=mp.work_hours,
        is_24_7=mp.is_24_7,
        experience_years=mp.experience_years,
        bio=mp.bio,
        price_call=float(mp.price_call) if mp.price_call is not None else None,
        price_diagnostics=float(mp.price_diagnostics) if mp.price_diagnostics is not None else None,
        price_repair_note=mp.price_repair_note,
        member_year=mp.created_at.year if mp.created_at else None,
    )


def _rank(mp: MasterProfile) -> tuple:
    # Verified first, then more experience, then newest.
    return (0 if mp.is_verified else 1, -(mp.experience_years or 0), -mp.id)


@router.get("", response_model=list[MasterPublicOut])
async def list_masters(
    session: SessionDep,
    specialization: str | None = Query(default=None),
    truck: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[MasterPublicOut]:
    # Only active masters who have actually filled a service profile.
    result = await session.execute(
        select(MasterProfile)
        .where(MasterProfile.status == MasterStatus.active, MasterProfile.specializations != "")
        .options(selectinload(MasterProfile.user))
    )
    masters = list(result.scalars().unique().all())

    if specialization:
        masters = [m for m in masters if specialization in _split(m.specializations)]
    if truck:
        masters = [m for m in masters if truck in _split(m.trucks)]
    if q:
        needle = q.strip().lower()
        masters = [
            m for m in masters
            if m.user and needle in f"{m.user.first_name} {m.user.last_name or ''}".lower()
        ]

    masters.sort(key=_rank)
    return [serialize_public(m) for m in masters]


@router.get("/{master_id}", response_model=MasterPublicOut)
async def get_master(master_id: int, session: SessionDep) -> MasterPublicOut:
    mp = (
        await session.execute(
            select(MasterProfile)
            .where(MasterProfile.id == master_id, MasterProfile.status == MasterStatus.active)
            .options(selectinload(MasterProfile.user))
        )
    ).scalar_one_or_none()
    if mp is None:
        raise HTTPException(status_code=404, detail="master_not_found")
    return serialize_public(mp)
