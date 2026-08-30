from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import CurrentUser, SessionDep
from app.models.master import BonusTransaction, MasterProfile, Payout
from app.schemas.master import BonusTxnOut, MasterOut, MasterRegister, PayoutOut
from app.services.master_service import MasterInput, register_or_update_master
from app.services.media import media_url

router = APIRouter(prefix="/master", tags=["master"])


def serialize_master(mp: MasterProfile) -> MasterOut:
    return MasterOut(
        id=mp.id,
        status=mp.status.value,
        photo=media_url(mp.photo),
        address=mp.address,
        card_number=mp.card_number,
        balance=float(mp.balance or 0),
        pending=float(mp.pending or 0),
        total_earned=float(mp.total_earned or 0),
        next_payout_at=mp.next_payout_at.isoformat() if mp.next_payout_at else None,
    )


@router.post("/register", response_model=MasterOut)
async def register(payload: MasterRegister, session: SessionDep, user: CurrentUser) -> MasterOut:
    if user.onboarded and user.master_profile is None:
        # Role is chosen once at first run; an onboarded buyer cannot become a master later.
        raise HTTPException(status_code=403, detail="role_locked")
    mp = await register_or_update_master(
        session,
        user,
        MasterInput(
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
            photo=payload.photo,
            address=payload.address,
            card_number=payload.card_number,
        ),
    )
    await session.commit()
    await session.refresh(mp)
    return serialize_master(mp)


@router.get("", response_model=MasterOut)
async def my_master(user: CurrentUser) -> MasterOut:
    if user.master_profile is None:
        raise HTTPException(status_code=404, detail="not_a_master")
    return serialize_master(user.master_profile)


@router.get("/transactions", response_model=list[BonusTxnOut])
async def my_transactions(session: SessionDep, user: CurrentUser) -> list[BonusTxnOut]:
    if user.master_profile is None:
        raise HTTPException(status_code=404, detail="not_a_master")
    result = await session.execute(
        select(BonusTransaction)
        .where(BonusTransaction.master_id == user.master_profile.id)
        .order_by(BonusTransaction.id.desc())
        .limit(100)
    )
    return [
        BonusTxnOut(
            id=t.id,
            amount=float(t.amount),
            status=t.status.value,
            order_id=t.order_id,
            note=t.note,
            created_at=t.created_at.isoformat() if t.created_at else "",
        )
        for t in result.scalars().all()
    ]


@router.get("/payouts", response_model=list[PayoutOut])
async def my_payouts(session: SessionDep, user: CurrentUser) -> list[PayoutOut]:
    if user.master_profile is None:
        raise HTTPException(status_code=404, detail="not_a_master")
    result = await session.execute(
        select(Payout)
        .where(Payout.master_id == user.master_profile.id)
        .order_by(Payout.id.desc())
        .limit(100)
    )
    return [
        PayoutOut(
            id=p.id,
            amount=float(p.amount),
            card_number=p.card_number,
            status=p.status.value,
            created_at=p.created_at.isoformat() if p.created_at else "",
        )
        for p in result.scalars().all()
    ]
