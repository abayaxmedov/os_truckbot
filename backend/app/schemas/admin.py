from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name_ru: str
    name_uz: str = ""
    slug: str | None = None
    parent_id: int | None = None
    commission_override: float | None = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name_ru: str | None = None
    name_uz: str | None = None
    slug: str | None = None
    parent_id: int | None = None
    commission_override: float | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CommissionUpdate(BaseModel):
    default_percent: float | None = Field(default=None, ge=0, le=100)


class SupportTelegramUpdate(BaseModel):
    support_telegram: str = Field(default="", max_length=64)


class SellerCommissionUpdate(BaseModel):
    commission_override: float | None = Field(default=None, ge=0, le=100)


class SellerStatusUpdate(BaseModel):
    status: str  # active | blocked | pending


class BannerIn(BaseModel):
    title: str = ""
    image: str
    target: str = ""
    is_active: bool = True
    sort_order: int = 0


class BannerOut(BaseModel):
    id: int
    title: str = ""
    image: str
    target: str = ""
    is_active: bool = True
    sort_order: int = 0


class AnalogNumberIn(BaseModel):
    number: str
    brand: str = ""
    is_original: bool = False


class AnalogGroupIn(BaseModel):
    title: str = ""
    numbers: list[AnalogNumberIn]


class AnalogReferenceOut(BaseModel):
    id: int
    number: str
    number_raw: str = ""
    brand: str = ""
    is_original: bool = False


class AnalogGroupOut(BaseModel):
    id: int
    title: str = ""
    references: list[AnalogReferenceOut] = []


class AdminStatsOut(BaseModel):
    orders_count: int
    sales_total: float
    commission_total: float
    payout_total: float
    customers_count: int
    sellers_count: int
    products_count: int
    popular_products: list[dict] = []


class AdminSellerOut(BaseModel):
    id: int
    user_id: int
    telegram_id: int
    shop_name: str
    status: str
    rating: float
    orders_count: int
    products_count: int
    commission_override: float | None = None


class AdminMasterOut(BaseModel):
    id: int
    user_id: int
    telegram_id: int
    name: str = ""
    phone: str = ""
    photo: str = ""
    status: str
    is_verified: bool = False
    trucks: list[str] = []
    specializations: list[str] = []
    regions: str = ""
    experience_years: int | None = None


class MasterVerifyUpdate(BaseModel):
    is_verified: bool


class ProductModerate(BaseModel):
    status: str  # approved | rejected
