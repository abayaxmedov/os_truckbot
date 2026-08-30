from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import user_to_out
from app.core.deps import CurrentUser, SessionDep
from app.models.enums import Language
from app.schemas.auth import UserOut, UserUpdate
from app.schemas.master import OnboardRequest

router = APIRouter(prefix="/me", tags=["me"])

_REFRESH = ["seller_profile", "master_profile"]


@router.get("", response_model=UserOut)
async def read_me(user: CurrentUser) -> UserOut:
    return user_to_out(user)


@router.patch("", response_model=UserOut)
async def update_me(payload: UserUpdate, user: CurrentUser, session: SessionDep) -> UserOut:
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.language in ("ru", "uz"):
        user.language = Language(payload.language)
    await session.commit()
    await session.refresh(user, attribute_names=_REFRESH)
    return user_to_out(user)


@router.post("/onboard", response_model=UserOut)
async def onboard(payload: OnboardRequest, user: CurrentUser, session: SessionDep) -> UserOut:
    """Mark first-run onboarding done. `role=master` still needs /master/register."""
    user.onboarded = True
    await session.commit()
    await session.refresh(user, attribute_names=_REFRESH)
    return user_to_out(user)
