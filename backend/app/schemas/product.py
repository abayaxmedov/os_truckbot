from __future__ import annotations

from pydantic import BaseModel, Field


class ProductImageOut(BaseModel):
    id: int
    url: str
    sort_order: int = 0


class VehicleOut(BaseModel):
    id: int
    brand_id: int
    brand_name: str
    model_id: int | None = None
    model_name: str | None = None


class SellerBrief(BaseModel):
    id: int
    shop_name: str
    rating: float = 0.0
    reviews_count: int = 0
    orders_count: int = 0
    completion_rate: float = 0.0


class ProductListItem(BaseModel):
    id: int
    name: str
    article: str = ""
    oem_number: str = ""
    part_brand: str = ""
    price: float
    currency: str = "UZS"
    stock_qty: int = 0
    in_stock: bool = True
    image: str | None = None
    category_id: int
    seller: SellerBrief | None = None
    status: str = "approved"
    bonus: float = 0.0  # master (usta) bonus per unit


class ProductOut(ProductListItem):
    name_ru: str
    name_uz: str = ""
    description: str = ""
    description_ru: str = ""
    description_uz: str = ""
    warranty: str = ""
    engine: str = ""
    is_active: bool = True
    images: list[ProductImageOut] = []
    vehicles: list[VehicleOut] = []


class VehicleIn(BaseModel):
    truck_brand_id: int
    truck_model_id: int | None = None


class ProductCreate(BaseModel):
    category_id: int
    name_ru: str
    name_uz: str = ""
    article: str = ""
    oem_number: str = ""
    part_brand: str = ""
    engine: str = ""
    description_ru: str = ""
    description_uz: str = ""
    price: float = Field(ge=0)
    stock_qty: int = Field(default=0, ge=0)
    warranty: str = ""
    vehicles: list[VehicleIn] = []


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name_ru: str | None = None
    name_uz: str | None = None
    article: str | None = None
    oem_number: str | None = None
    part_brand: str | None = None
    engine: str | None = None
    description_ru: str | None = None
    description_uz: str | None = None
    price: float | None = Field(default=None, ge=0)
    stock_qty: int | None = Field(default=None, ge=0)
    warranty: str | None = None
    bonus: float | None = Field(default=None, ge=0)
    is_active: bool | None = None
    vehicles: list[VehicleIn] | None = None
