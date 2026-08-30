from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: int, extra: dict | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises jwt.PyJWTError on invalid / expired tokens."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
