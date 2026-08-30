from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from urllib.parse import parse_qsl


class InitDataError(ValueError):
    """Raised when Telegram WebApp initData is missing/invalid."""


@dataclass
class TelegramUser:
    id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    language_code: str = ""
    photo_url: str = ""


def _data_check_string(pairs: list[tuple[str, str]]) -> str:
    """Build the data-check-string: all pairs except `hash`, sorted, joined by \\n.

    Only `hash` is excluded. Telegram computes the HMAC over every other field it
    sends — including `signature` (present on modern mobile clients) — so excluding
    `signature` here would break validation for real initData.
    """
    filtered = [(k, v) for k, v in pairs if k != "hash"]
    filtered.sort(key=lambda kv: kv[0])
    return "\n".join(f"{k}={v}" for k, v in filtered)


def verify_init_data(init_data: str, bot_token: str) -> dict:
    """
    Validate Telegram Mini App `initData` (HMAC-SHA256 scheme).

    Returns the parsed fields dict (with `user` decoded from JSON) on success.
    Raises InitDataError on any failure.

    Docs: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data:
        raise InitDataError("empty initData")
    if not bot_token:
        raise InitDataError("bot token is not configured")

    pairs = parse_qsl(init_data, keep_blank_values=True)
    data = dict(pairs)
    received_hash = data.get("hash")
    if not received_hash:
        raise InitDataError("initData has no hash")

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    check_string = _data_check_string(pairs)
    computed = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        raise InitDataError("initData hash mismatch")

    if "user" in data:
        try:
            data["user"] = json.loads(data["user"])
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise InitDataError("invalid user payload") from exc
    return data


def parse_user(init_data_fields: dict) -> TelegramUser:
    raw = init_data_fields.get("user")
    if not isinstance(raw, dict) or "id" not in raw:
        raise InitDataError("initData has no user")
    return TelegramUser(
        id=int(raw["id"]),
        first_name=raw.get("first_name", "") or "",
        last_name=raw.get("last_name", "") or "",
        username=raw.get("username", "") or "",
        language_code=raw.get("language_code", "") or "",
        photo_url=raw.get("photo_url", "") or "",
    )
