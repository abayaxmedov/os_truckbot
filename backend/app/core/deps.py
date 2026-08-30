from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import SellerProfile, User

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


async def get_optional_user(
    session: SessionDep,
    authorization: str | None = Header(default=None),
) -> User | None:
    token = _extract_bearer(authorization)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
    result = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.seller_profile), selectinload(User.master_profile))
    )
    return result.scalar_one_or_none()


async def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


async def get_current_seller(
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> SellerProfile:
    if user.seller_profile is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller profile required")
    return user.seller_profile


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
CurrentSeller = Annotated[SellerProfile, Depends(get_current_seller)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
