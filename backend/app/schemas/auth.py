from __future__ import annotations

from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    init_data: str = ""
    # DEV ONLY (when DEV_AUTH_BYPASS=true): impersonate a Telegram user without initData
    dev_telegram_id: int | None = None
    dev_first_name: str | None = None


class SellerBrief(BaseModel):
    id: int
    shop_name: str
    status: str
    rating: float
    reviews_count: int


class MasterBrief(BaseModel):
    id: int
    balance: float = 0.0
    pending: float = 0.0
    status: str = "active"


class UserOut(BaseModel):
    id: int
    telegram_id: int
    username: str
    first_name: str
    last_name: str
    phone: str | None = None
    language: str
    is_admin: bool
    is_seller: bool
    is_master: bool = False
    onboarded: bool = False
    seller: SellerBrief | None = None
    master: MasterBrief | None = None


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    language: str | None = None
