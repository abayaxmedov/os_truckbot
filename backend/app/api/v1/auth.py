from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.deps import CurrentUser, SessionDep
from app.core.security import create_access_token
from app.core.telegram_auth import InitDataError, TelegramUser, parse_user, verify_init_data
from app.models.enums import Language
from app.models.user import User
from app.schemas.auth import AuthResponse, MasterBrief, SellerBrief, TelegramAuthRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("auth.debug")


def user_to_out(user: User) -> UserOut:
    seller = None
    if user.seller_profile is not None:
        sp = user.seller_profile
        seller = SellerBrief(
            id=sp.id,
            shop_name=sp.shop_name,
            status=sp.status.value,
            rating=float(sp.rating or 0),
            reviews_count=sp.reviews_count,
        )
    master = None
    if user.master_profile is not None:
        mp = user.master_profile
        master = MasterBrief(
            id=mp.id,
            balance=float(mp.balance or 0),
            pending=float(mp.pending or 0),
            status=mp.status.value,
        )
    return UserOut(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        language=user.language.value,
        is_admin=user.is_admin,
        is_seller=user.seller_profile is not None,
        is_master=user.master_profile is not None,
        onboarded=user.onboarded,
        seller=seller,
        master=master,
    )


async def upsert_user(session, tg: TelegramUser) -> User:
    result = await session.execute(
        select(User)
        .where(User.telegram_id == tg.id)
        .options(selectinload(User.seller_profile), selectinload(User.master_profile))
    )
    user = result.scalar_one_or_none()
    if user is None:
        lang = Language.uz if tg.language_code == "uz" else Language(settings.default_language)
        user = User(
            telegram_id=tg.id,
            username=tg.username,
            first_name=tg.first_name,
            last_name=tg.last_name,
            language=lang,
            is_admin=tg.id in settings.admin_ids,
        )
        session.add(user)
        await session.flush()
    else:
        user.username = tg.username or user.username
        user.first_name = tg.first_name or user.first_name
        user.last_name = tg.last_name or user.last_name
        if tg.id in settings.admin_ids:
            user.is_admin = True
    await session.commit()
    await session.refresh(user, attribute_names=["seller_profile", "master_profile"])
    return user


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(payload: TelegramAuthRequest, session: SessionDep) -> AuthResponse:
    tg: TelegramUser | None = None

    if payload.init_data:
        try:
            fields = verify_init_data(payload.init_data, settings.bot_token)
            tg = parse_user(fields)
        except InitDataError as exc:
            logger.warning("initData validation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid_init_data:{exc}"
            ) from exc
    elif settings.dev_auth_bypass and payload.dev_telegram_id:
        tg = TelegramUser(
            id=payload.dev_telegram_id,
            first_name=payload.dev_first_name or "Dev",
            username=f"dev{payload.dev_telegram_id}",
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="init_data_required")

    user = await upsert_user(session, tg)
    token = create_access_token(user.id)
    return AuthResponse(token=token, user=user_to_out(user))


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser) -> UserOut:
    return user_to_out(user)
