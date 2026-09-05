from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import SessionDep
from app.models.enums import MasterStatus
from app.models.master import MasterProfile
from app.schemas.master import DistanceOut, DistanceRequest, MasterPublicOut
from app.services.media import media_url

router = APIRouter(prefix="/masters", tags=["masters"])

# Rough on-the-road speed for a service call (km/h) → ETA. Deliberately conservative.
_AVG_SPEED_KMH = 28.0


def _split(csv: str) -> list[str]:
    return [c for c in (csv or "").split(",") if c]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0  # Earth radius (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


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
        has_location=mp.latitude is not None and mp.longitude is not None,
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


@router.post("/distances", response_model=list[DistanceOut])
async def master_distances(payload: DistanceRequest, session: SessionDep) -> list[DistanceOut]:
    """Distance + rough ETA from the client's location to each master's base.

    The client location arrives in the body (never the URL). Master coordinates
    are used server-side only and never exposed to the client.
    """
    stmt = select(MasterProfile).where(
        MasterProfile.status == MasterStatus.active,
        MasterProfile.latitude.is_not(None),
        MasterProfile.longitude.is_not(None),
    )
    if payload.ids:
        stmt = stmt.where(MasterProfile.id.in_(payload.ids))
    masters = list((await session.execute(stmt)).scalars().all())

    out: list[DistanceOut] = []
    for m in masters:
        km = _haversine_km(payload.latitude, payload.longitude, float(m.latitude), float(m.longitude))
        eta = max(3, round(km / _AVG_SPEED_KMH * 60))
        out.append(DistanceOut(id=m.id, distance_km=round(km, 1), eta_min=eta))
    out.sort(key=lambda d: d.distance_km)
    return out


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
