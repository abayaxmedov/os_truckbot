from __future__ import annotations

from pydantic import BaseModel


class SellerRegister(BaseModel):
    shop_name: str
    description: str = ""


class SellerOut(BaseModel):
    id: int
    user_id: int
    shop_name: str
    description: str = ""
    status: str
    rating: float = 0.0
    orders_count: int = 0
    reviews_count: int = 0
    completion_rate: float = 0.0
    commission_override: float | None = None


class SellerStatsOut(BaseModel):
    sales_total: float = 0.0
    commission_total: float = 0.0
    payout_total: float = 0.0
    orders_count: int = 0
    products_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    completion_rate: float = 0.0


class ImportResult(BaseModel):
    created: int
    errors: list[dict] = []
