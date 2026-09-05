from __future__ import annotations

from pydantic import BaseModel


class MasterRegister(BaseModel):
    first_name: str
    last_name: str = ""
    phone: str = ""
    photo: str = ""  # media path from /uploads/image
    address: str = ""
    card_number: str = ""
    # Service profile (B1)
    trucks: list[str] = []
    specializations: list[str] = []
    regions: str = ""
    work_hours: str = ""
    is_24_7: bool = False
    experience_years: int | None = None
    bio: str = ""
    price_call: float | None = None
    price_diagnostics: float | None = None
    price_repair_note: str = ""
    latitude: float | None = None
    longitude: float | None = None


class MasterOut(BaseModel):
    id: int
    status: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    photo: str = ""
    address: str = ""
    card_number: str = ""
    balance: float = 0.0
    pending: float = 0.0
    total_earned: float = 0.0
    next_payout_at: str | None = None
    # Service profile (B1)
    trucks: list[str] = []
    specializations: list[str] = []
    regions: str = ""
    work_hours: str = ""
    is_24_7: bool = False
    experience_years: int | None = None
    bio: str = ""
    price_call: float | None = None
    price_diagnostics: float | None = None
    price_repair_note: str = ""
    is_verified: bool = False
    latitude: float | None = None
    longitude: float | None = None


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


class MasterPublicOut(BaseModel):
    """Master profile as seen by clients in the 'find a master' directory."""

    id: int
    name: str = ""
    photo: str = ""
    phone: str = ""
    is_verified: bool = False
    trucks: list[str] = []
    specializations: list[str] = []
    regions: str = ""
    work_hours: str = ""
    is_24_7: bool = False
    experience_years: int | None = None
    bio: str = ""
    price_call: float | None = None
    price_diagnostics: float | None = None
    price_repair_note: str = ""
    member_year: int | None = None
    has_location: bool = False  # whether distance-to-me can be computed


class DistanceRequest(BaseModel):
    """Client shares its location (in the body, never the URL) to get distances."""

    latitude: float
    longitude: float
    ids: list[int] | None = None  # limit to these masters (optional)


class DistanceOut(BaseModel):
    id: int
    distance_km: float
    eta_min: int


class OnboardRequest(BaseModel):
    role: str  # "buyer" | "master"


class AdminPayoutOut(PayoutOut):
    master_id: int
    master_name: str = ""
    phone: str = ""


class ProductBonusUpdate(BaseModel):
    bonus: float
