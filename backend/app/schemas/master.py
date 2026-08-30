from __future__ import annotations

from pydantic import BaseModel


class MasterRegister(BaseModel):
    first_name: str
    last_name: str = ""
    phone: str = ""
    photo: str = ""  # media path from /uploads/image
    address: str = ""
    card_number: str = ""


class MasterOut(BaseModel):
    id: int
    status: str
    photo: str = ""
    address: str = ""
    card_number: str = ""
    balance: float = 0.0
    pending: float = 0.0
    total_earned: float = 0.0
    next_payout_at: str | None = None


class BonusTxnOut(BaseModel):
    id: int
    amount: float
    status: str
    order_id: int | None = None
    note: str = ""
    created_at: str


class PayoutOut(BaseModel):
    id: int
    amount: float
    card_number: str = ""
    status: str
    created_at: str


class OnboardRequest(BaseModel):
    role: str  # "buyer" | "master"


class AdminPayoutOut(PayoutOut):
    master_id: int
    master_name: str = ""
    phone: str = ""


class ProductBonusUpdate(BaseModel):
    bonus: float
